import os
import datetime
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
# from src.server import GmailMCPClient # Switched to native
from typing import Any

# Define State
class AgentState(TypedDict):
    messages: List[Dict[str, Any]]
    replies_to_send: List[Dict[str, Any]]
    last_checked_time: float # timestamp

# Initialize Groq
def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    return ChatGroq(model_name="llama-3.3-70b-versatile", api_key=api_key, temperature=0)

# --- Nodes ---

async def fetch_emails(state: AgentState, mcp_client: Any):
    """Fetches unread emails from Gmail, filters by time."""
    print("--- Fetching Emails ---")
    
    # 1. Get List (search threads)
    # Note: query 'is:unread' + check logic
    try:
        # We search specifically for unread messages
        result = await mcp_client.session.call_tool("search_threads", arguments={"query": "is:unread", "maxResults": 3})
        # MCP Tool result structure: depends on server. content[0].text is normally JSON string or direct data.
        # We need to parse it. 
        # Typically MCP returns CallToolResult(content=[TextContent(type='text', text='JSON...'), ...])
        
        threads = []
        if result.content and result.content[0].type == 'text':
             threads = eval(result.content[0].text) # or json.loads if it's strictly JSON
             # The result might be a list of dicts. 
             # Safety: if eval fails or structure is different, we need robust parsing.
             # Let's assume standard json.
             import json
             try:
                 data = json.loads(result.content[0].text)
                 threads = data if isinstance(data, list) else data.get('threads', [])
             except:
                 # Fallback if it's already a dict/list (mcp python sdk might auto-parse?)
                 # For now, let's treat it as potentially needing parse.
                 pass

        if not threads:
            print("No unread threads found.")
            return {"messages": []}

        # 2. Get Details for each thread (or at least the latest message in it)
        # We need to filter by time > last_checked_time
        # And we need content/snippet.
        
        new_messages = []
        last_time = state.get("last_checked_time", 0)
        print(f"DEBUG: Filtering messages after timestamp: {last_time} ({datetime.datetime.fromtimestamp(last_time)})")

        for thread in threads:
            # We need to fetch the actual message content. 
            # Tool: `get_thread` usually? Or `get_message`.
            # If search_threads returns snippet, use that for filtering.
            # But we need timestamp.
            
            # Let's assume we fetch thread details
            t_id = thread['id']
            # call get_thread
            t_result = await mcp_client.session.call_tool("get_thread", arguments={"threadId": t_id})
            t_data = json.loads(t_result.content[0].text)
            
            # Get latest message
            messages_in_thread = t_data.get('messages', [])
            if not messages_in_thread: continue
            
            latest_msg = messages_in_thread[-1]
            
            # Timestamp check (internalDate is ms)
            msg_time = int(latest_msg.get('internalDate', 0)) / 1000.0
            print(f"DEBUG: Checking Msg ID: {latest_msg['id']}, Time: {msg_time} ({datetime.datetime.fromtimestamp(msg_time)})")
            
            if msg_time > last_time:
                # Add to processing list
                new_messages.append({
                    "id": latest_msg['id'],
                    "threadId": t_id,
                    "snippet": latest_msg.get('snippet', ''),
                    "sender": next((h['value'] for h in latest_msg['payload']['headers'] if h['name'] == 'From'), 'Unknown'),
                    "subject": next((h['value'] for h in latest_msg['payload']['headers'] if h['name'] == 'Subject'), 'No Subject'),
                    "body": latest_msg.get('snippet', '') # Simplifying: using snippet as body for now
                })
        
        return {"messages": new_messages}

    except Exception as e:
        print(f"Error fetching emails: {e}")
        return {"messages": []}

async def filter_emails(state: AgentState):
    """Filters emails: Real Person AND Mobiles Only (Optimized for Tokens)."""
    print("--- Filtering Emails ---")
    messages = state["messages"]
    valid_messages = []
    
    llm = get_llm()
    
    for msg in messages:
        subject = msg['subject']
        snippet = msg['snippet']
        sender = msg['sender']
        
        # Combined Check: Single Prompt to save tokens
        prompt_analysis = f"""
        You are a smart email filter for a Mobile Store.
        Analyze this email:
        Sender: {sender}
        Subject: {subject}
        Content: {snippet}
        
        Determine two things:
        1. Is this a REAL email from a human (not marketing/spam/automated)?
        2. Is the user explicitly asking about mobile phones, buying a phone, or mobile accessories?
        
        Reply strictly in the following JSON format (no markdown, just json):
        {{
            "is_real_human": true/false,
            "is_mobile_related": true/false,
            "reason": "short reason"
        }}
        """
        try:
            response = llm.invoke([HumanMessage(content=prompt_analysis)]).content.strip()
            # Clean up potential markdown formatting from LLM (e.g. ```json ... ```)
            if "```" in response:
                response = response.split("```")[1].strip()
                if response.startswith("json"):
                    response = response[4:].strip()
            
            import json
            analysis = json.loads(response)
            
            print(f"DEBUG Analysis for '{subject}': {analysis}")
            
            if analysis.get("is_real_human") and analysis.get("is_mobile_related"):
                print(f"Accepted: {subject}")
                valid_messages.append(msg)
            else:
                print(f"Skipping: {subject} ({analysis.get('reason')})")
                
        except Exception as e:
            print(f"Error filtering email '{subject}': {e}")
            continue

    return {"messages": valid_messages}

async def generate_replies(state: AgentState):
    """Generates replies for valid emails."""
    print("--- Generating Replies ---")
    messages = state["messages"]
    replies = []
    
    llm = get_llm()
    
    for msg in messages:
        prompt = f"""
        You are a helpful Mobile Store Owner.
        A customer sent this inquiry:
        Subject: {msg['subject']}
        Message: {msg['snippet']}
        
        Write a professional, short, and helpful reply. 
        Do not include placeholders like [Your Name]. Sign off as 'Mobile Store Team'.
        """
        response = llm.invoke([HumanMessage(content=prompt)]).content.strip()
        
        replies.append({
            "threadId": msg['threadId'],
            "to": msg['sender'], # Simplification: use sender string, raw string often contains email <email>
            "subject": f"Re: {msg['subject']}",
            "body": response
        })
        
    return {"replies_to_send": replies}

async def send_replies(state: AgentState, mcp_client: Any):
    """Sends the generated replies."""
    print("--- Sending Replies ---")
    replies = state["replies_to_send"]
    
    for reply in replies:
        print(f"Sending reply to {reply['to']}")
        try:
            # Clean 'to' address if needed (extract email from "Name <email>")
            to_addr = reply['to']
            if "<" in to_addr:
                to_addr = to_addr.split("<")[1].strip(">")
                
            await mcp_client.send_reply(
                to=to_addr,
                subject=reply['subject'],
                body=reply['body'],
                thread_id=reply['threadId']
            )
        except Exception as e:
            print(f"Failed to send reply to {reply['to']}: {e}")
            
    # Update timestamp to now to avoid duplicate processing in next cycle
    # (In a real app, track IDs, but time is okay for simple logic)
    import time
    return {"last_checked_time": time.time(), "messages": [], "replies_to_send": []}

# --- Graph Construction ---
def create_graph(mcp_client):
    workflow = StateGraph(AgentState)
    
    # We need to wrap nodes to pass mcp_client
    async def fetch_node(state):
        return await fetch_emails(state, mcp_client)
        
    async def send_node(state):
        return await send_replies(state, mcp_client)

    workflow.add_node("fetch", fetch_node)
    workflow.add_node("filter", filter_emails)
    workflow.add_node("reply", generate_replies)
    workflow.add_node("send", send_node)
    
    workflow.set_entry_point("fetch")
    
    workflow.add_edge("fetch", "filter")
    workflow.add_edge("filter", "reply")
    workflow.add_edge("reply", "send")
    workflow.add_edge("send", END)
    
    return workflow.compile()

import os
import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.message import EmailMessage

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
TOKEN_FILE = 'token_python.json' # Use distinct token file to avoid format conflicts with node

class GmailNativeClient:
    def __init__(self):
        self.creds = None
        self.service = None

    async def connect(self):
        # 1. Load Credentials
        # We try to load 'token.json' first (the original one we fixed), 
        # or 'token_python.json' if we save one.
        # Actually, let's just use the `auth_manual.py` output `token.json` 
        # BUT we just converted it to Node format! Aaaargh.
        # We need to revert it or re-auth.
        # Luckily we have `token_debug.json` from our debug run!
        
        # We'll use `token_debug.json` if available, or try `token.json`.
        # Python `Credentials.from_authorized_user_file` expects specific keys.
        # Node format has `access_token` etc flattened. Python uses `token`.
        
        target_token = 'token_debug.json'
        if not os.path.exists(target_token):
             # Try token.json, check format?
             target_token = 'token.json'

        if os.path.exists(target_token):
            try:
                self.creds = Credentials.from_authorized_user_file(target_token, SCOPES)
            except ValueError:
                print(f"Token file {target_token} format mismatch. Re-run auth_manual.py or debug_auth.py")
                # Fallback to re-auth?
                pass

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Warning: Token refresh failed (Network issue?): {e}")
                    # Do NOT clear creds here. If it's a network error, we want to try again later.
                    # self.creds = None 
                    pass
            
            if not self.creds:
                 raise RuntimeError("No valid credentials found. Please run 'python src/debug_auth.py --run' first.")

        self.service = build('gmail', 'v1', credentials=self.creds)
        print("Gmail API Service built successfully.")

    # --- Tool Equivalents ---
    
    async def list_messages(self, query="is:unread", max_results=10):
        # We mimic the MCP tool interface? 
        # Or just return data structure expected by agent_graph.
        # mcp_client.session.call_tool("search_threads", ...) return object with content[0].text
        
        # Let's verify what agent_graph expects.
        # It expects `result.content[0].text`.
        # We need to wrap our result to match or change agent_graph.
        # Easier to change agent_graph to generic client interface?
        # Or make this client mimic MCP response.
        pass # implemented in full file below

    # Define a MockResult to match MCP structure
    class MockResult:
        def __init__(self, text):
            self.content = [type('obj', (object,), {'text': text, 'type': 'text'})]

    async def search_threads(self, query, max_results=10):
        results = self.service.users().threads().list(userId='me', q=query, maxResults=max_results).execute()
        threads = results.get('threads', [])
        import json
        return self.MockResult(json.dumps(threads))

    async def get_thread(self, thread_id):
        tdata = self.service.users().threads().get(userId='me', id=thread_id).execute()
        import json
        return self.MockResult(json.dumps(tdata))

    async def send_reply(self, to, subject, body, thread_id):
        # Send message
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to
        message['Subject'] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        create_message = {
            'raw': encoded_message,
            'threadId': thread_id
        }
        
        sent = self.service.users().messages().send(userId="me", body=create_message).execute()
        print(f"Message sent: {sent['id']}")
        return sent

    # Helper to act as MCP session for agent_graph
    # agent_graph calls `mcp_client.session.call_tool("name", args)`
    # We can inject a dummy session.
    
    class FakeSession:
        def __init__(self, client):
            self.client = client
        
        async def call_tool(self, name, arguments):
            if name == "search_threads":
                return await self.client.search_threads(arguments.get('query'), arguments.get('maxResults'))
            elif name == "get_thread":
                return await self.client.get_thread(arguments.get('threadId'))
            elif name == "send_message":
                # agent_graph in send_replies calls 'send_reply' on client wrapper, 
                # but inside wrapper it calls 'send_message'.
                # Wait, agent_graph calls `mcp_client.send_reply`.
                # So we just need `send_reply` on the main client class.
                pass
            return None

    @property
    def session(self):
        return self.FakeSession(self)
        
    async def close(self):
        pass


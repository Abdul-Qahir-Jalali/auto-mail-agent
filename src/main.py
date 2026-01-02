import asyncio
import time
import os
from dotenv import load_dotenv
from src.gmail_client_native import GmailNativeClient
from src.agent_graph import create_graph

# Load env variables from .env
load_dotenv()

async def main():
    print("Starting Auto Mail Agent (Native Mode)...")
    print(f"Time: {time.ctime()}")

    # Initialize Client
    client = GmailNativeClient()
    
    try:
        await client.connect()
        print("MCP Client Connected.")
        
        # Build Graph
        graph = create_graph(client)
        
        # Initialize State
        # We start checking from NOW. Old emails are ignored.
        state = {
            "messages": [],
            "replies_to_send": [],
            "last_checked_time": time.time() - 86400 # Look back 24 hours to catch recent test emails
        }
        
        print(f"Agent Active. Filter Start Time: {state['last_checked_time']}")
        print("Waiting for new emails... (Ctrl+C to stop)")
        
        while True:
            # Run the graph
            # invoke returns the final state
            new_state = await graph.ainvoke(state)
            
            # Update state for next iteration (crucially, the timestamp)
            state["last_checked_time"] = new_state.get("last_checked_time", time.time())
            
            # Sleep
            sleep_time = 60
            print(f"Cycle Complete. Sleeping for {sleep_time}s...")
            await asyncio.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("Stopping Agent...")
    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        await client.close()
        print("Agent Stopped.")

if __name__ == "__main__":
    asyncio.run(main())

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDS_FILE = 'credentials.json'

def main():
    if not os.path.exists(CREDS_FILE):
        print(f"Error: {CREDS_FILE} not found!")
        return

    print(f"Loading {CREDS_FILE}...")
    try:
        with open(CREDS_FILE, 'r') as f:
            creds_data = json.load(f)
            client_type = 'installed' if 'installed' in creds_data else 'web'
            print(f"Client Type detected: {client_type}")
            if client_type == 'installed':
                redirect_uris = creds_data['installed'].get('redirect_uris', [])
                print(f"Configured Redirect URIs: {redirect_uris}")
            
    except Exception as e:
        print(f"Error reading credentials file: {e}")
        return

    print("\n--- Initializing Flow ---")
    flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
    
    # 1. Print what the library generates for a random port
    print("\n[Test 1] Generating URL with default behavior (random port)...")
    flow.redirect_uri = "http://localhost" # Just setting a base to see
    auth_url, _ = flow.authorization_url(prompt='consent')
    print(f"Example Auth URL (Manual generation): {auth_url}")
    
    # 2. Try running with a Fixed Port (8080)
    # If the user has 'http://localhost' whitelisted, 
    # sometimes specific ports are needed or the random one is blocked by a strict policy?
    # Usually for 'installed' apps, random ports on localhost are allowed.
    
    print("\n[Test 2] Attempting to run local server on FIXED port 8080...")
    print("If this fails, it might be because port 8080 is in use or blocked.")
    try:
        # Note: This will block until the user authenticates or we kill it.
        # Since we are running this as a tool, we might timeout if the user doesn't interact.
        # So we won't actually block here in this debug script for long, 
        # but we'll print the instructions.
        pass
        # executing run_local_server here would block effectively.
        # we will skip the blocking call in this non-interactive debug run
        # unless user runs it manually.
        
    except Exception as e:
        print(f"Setup failed: {e}")

    print("\nTo test actual auth, run this command in your terminal:")
    print("python src/debug_auth.py --run")

if __name__ == '__main__':
    import sys
    if '--run' in sys.argv:
        flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
        print("Starting server on port 8080...")
        try:
            creds = flow.run_local_server(port=8080)
            print("Success! Token received.")
            with open('token_debug.json', 'w') as f:
                f.write(creds.to_json())
            print("Saved to token_debug.json")
        except Exception as e:
            print(f"Failed: {e}")
    else:
        main()

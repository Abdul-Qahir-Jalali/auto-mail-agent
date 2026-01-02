import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def main():
    creds = None
    # 1. Check for existing token
    if os.path.exists(TOKEN_FILE):
        print(f"Token file {TOKEN_FILE} already exists. Deleting to force refresh.")
        os.remove(TOKEN_FILE)

    # 2. Load flow from credentials.json
    if not os.path.exists(CREDS_FILE):
        print(f"Error: {CREDS_FILE} not found!")
        return

    print("--- Starting Manual Authentication ---")
    flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
    
    # 3. Run Local Server Flow
    # This will open a browser window or print a local URL
    print("Opening browser for authentication on port 8080...")
    try:
        creds = flow.run_local_server(port=8080)
    except Exception as e:
        print(f"Browser flow failed: {e}")
        print("Please ensure you have a browser available or try checking firewall settings.")
        return
    
    # 4. Save Token
    print(f"Authentication successful!")
    print(f"Saving token to {TOKEN_FILE}...")
    
    # We save in the format that google libraries expect, assuming mcp server uses same.
    # Usually it's just the json dump of the creds.
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    
    print("Done. You can now run the agent.")

if __name__ == '__main__':
    main()

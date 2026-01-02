# Auto Mail Agent Setup Guide

Follow these steps exactly to get the necessary keys and files.

## Part 1: Get Google Cloud Credentials (for Gmail)

We need a `credentials.json` file to allow the agent to talk to your Gmail.

1.  **Go to Google Cloud Console**:
    - Open [https://console.cloud.google.com/](https://console.cloud.google.com/) in your browser.
    - Log in with the Gmail account you want to use.

2.  **Create a New Project**:
    - Click the project dropdown at the top left (next to "Google Cloud").
    - Click **"New Project"**.
    - Name it `AutoMailAgent` and click **Create**.
    - Wait for it to be created, then **Select** the project.

3.  **Enable Gmail API**:
    - In the search bar at the top, type `Gmail API` and select it.
    - Click **Enable**.

4.  **Configure OAuth Consent Screen**:
    - Go to **APIs & Services** > **OAuth consent screen** (via the side menu).
    - Select **External** (this is easier for personal testing) and click **Create**.
        - *Note: If "External" requires verification, choose "Internal" if you have a Google Workspace organization, but for personal @gmail.com, you must usually choose External.*
    - **App Information**:
        - App name: `AutoMail`
        - User support email: Select your email.
    - **Developer Contact Information**: Enter your email again.
    - Click **Save and Continue**.
    - **Scopes**: Click **Add or Remove Scopes**.
        - Search for `gmail.modify` or just select `https://mail.google.com/` (full access) to be safe, or specifically `https://www.googleapis.com/auth/gmail.send` and `https://www.googleapis.com/auth/gmail.readonly`.
        - For this agent, select `.../auth/gmail.modify` (reads and sends).
        - Click **Update**, then **Save and Continue**.
    - **Test Users**:
        - Click **Add Users**.
        - Enter **your own Gmail address** (the one you are logged in with). This is CRITICAL because the app is in "Testing" mode.
        - Click **Save and Continue**.

5.  **Create Credentials**:
    - Go to **APIs & Services** > **Credentials**.
    - Click **+ CREATE CREDENTIALS** > **OAuth client ID**.
    - **Application type**: Select **Desktop app**.
    - Name: `AutoMailClient`.
    - Click **Create**.

6.  **Download JSON**:
    - You will see a popup "OAuth client created".
    - Click the **Download JSON** button (looks like a down arrow).
    - Save this file as `credentials.json`.
    - **Action**: Move this `credentials.json` file into the folder: `d:\auto-mail-agent`.

## Part 2: Get Groq API Key (for the Brain)

1.  **Go to Groq Console**:
    - Open [https://console.groq.com/keys](https://console.groq.com/keys).
    - Log in or Sign up.

2.  **Create Key**:
    - Click **Create API Key**.
    - Name it `AutoMail`.
    - Copy the key (it starts with `gsk_...`).

3.  **Save in Project**:
    - I will create a `.env` file for you. You just need to paste the key there later, or tell me the key (if you trust this chat) and I can save it for you.
    - *Better security*: I will create a placeholder `.env` file, and you can paste it in yourself.

## Summary of Files You Need
By the end of this, you should have in `d:\auto-mail-agent`:
1.  `credentials.json` (From Google)
2.  `.env` (I will create this, you edit it with the Groq Key)

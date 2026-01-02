# Auto Mail Agent - Project Overview

## 📂 Project Structure

Verified files in your `d:\auto-mail-agent` directory:

| File / Folder          | Purpose                                                            |
| :--------------------- | :----------------------------------------------------------------- |
| **`run_agent.ps1`**    | **Start Here.** The script that runs your agent.                   |
| **`.env`**             | Stores your **Groq API Key**.                                      |
| **`credentials.json`** | Your **Google Cloud credentials** (downloaded from Google).        |
| **`token.json`**       | Your **login session**. Created after you log in. Keep this safe!  |
| **`src/`**             | The folder containing the code (see below).                        |
| **`auth_setup.ps1`**   | A helper script for setting up the environment (mostly for setup). |
| **`requirements.txt`** | List of Python libraries needed (langchain, google-api, etc).      |

### 🛠️ Source Code (`src/`)

| File                         | What it does                                                                                                       |
| :--------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| **`main.py`**                | The **Coordinator**. It sets up the loop (checks every 60s) and runs the "Brain".                                  |
| **`agent_graph.py`**         | The **"Brain"**. It decides what to do: detects new emails → checks if they are real → writes a reply -> sends it. |
| **`gmail_client_native.py`** | The **Hands**. It talks to Gmail to actually Read and Send emails.                                                 |
| **`debug_auth.py`**          | **Repair Tool**. Run this if you have login/token errors.                                                          |
| **`auth_manual.py`**         | Original login script (kept for backup).                                                                           |

## 🚀 How to Run

1.  **Open Terminal**: Go to `d:\auto-mail-agent`.
2.  **Run Script**:
    ```powershell
    .\run_agent.ps1
    ```
3.  **Process**:
    *   It wakes up every **60 seconds**.
    *   It checks the **Last 3 Unread Emails**.
    *   **Filter**: Checks if it's a "Real Human" AND about "Mobiles".
    *   **Action**: If yes, it sends a reply.

## 🔧 Troubleshooting

*   **"No valid credentials"**: Run `python src/debug_auth.py --run` to log in again.
*   **"Network Error"**: Check your internet. The agent will retry strictly.

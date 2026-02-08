import sys
import os
import time
from playwright.sync_api import sync_playwright

def save_session(platform_name: str, start_url: str):
    """
    Launches a browser for the user to login.
    Saves the session state (cookies) to 'sessions/{platform_name}.json'
    """
    session_dir = "sessions"
    os.makedirs(session_dir, exist_ok=True)
    session_file = os.path.join(session_dir, f"{platform_name}.json")
    
    print(f"\n[+] Starting Authentication for: {platform_name.upper()}")
    print(f"[*] Session will be saved to: {session_file}")
    print("------------------------------------------------")
    print("1. A browser window will open.")
    print("2. Log in to the website manually.")
    print("3. Deal with any 2FA/Captchas.")
    print("4. When you land on the feed/home page, CLOSE THE BROWSER via the 'X' button.")
    print("------------------------------------------------")
    # input("Press ENTER to launch browser...") # REMOVED BLOCKER

    with sync_playwright() as p:
        # Launch visually so user can interact
        # STEALTH ARGS: Hide "Chrome is being controlled by automated software"
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars"
            ],
            ignore_default_args=["--enable-automation"]
        )
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto(start_url)
            
            # Wait for user input to save
            print("\n" + "="*40)
            print("STEP 1: Log in in the browser window.")
            print("STEP 2: When you see your LinkedIn Feed...")
            print("STEP 3: COME BACK TO THIS CMD AND PRESS ENTER TO SAVE.")
            print("="*40)
            input("\n>>> PRESS ENTER HERE TO SAVE SESSION AND CLOSE BROWSER <<<")
            
        except Exception as e:
            print(f"[-] Error during auth wait: {e}")
            
        # Save state
        context.storage_state(path=session_file)
        print(f"\n[+] SUCCESS! Session saved to {session_file}")
        browser.close()

if __name__ == "__main__":
    print("Select Platform to Authenticate:")
    print("1. LinkedIn")
    print("2. X (Twitter)")
    choice = input("Enter number (1 or 2): ").strip()
    
    if choice == '1':
        save_session('linkedin', 'https://www.linkedin.com/login')
    elif choice == '2':
        save_session('x', 'https://twitter.com/i/flow/login')
    else:
        print("Invalid choice.")

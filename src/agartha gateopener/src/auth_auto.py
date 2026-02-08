import sys
from src.auth_maintainer import save_session

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/auth_auto.py [linkedin|x]")
        sys.exit(1)
        
    platform = sys.argv[1]
    if platform == 'linkedin':
        print("[*] Auto-launching LinkedIn Auth...")
        save_session('linkedin', 'https://www.linkedin.com/login')
    elif platform == 'x':
        print("[*] Auto-launching X (Twitter) Auth...")
        save_session('x', 'https://twitter.com/i/flow/login')
    else:
        print(f"Unknown platform: {platform}")

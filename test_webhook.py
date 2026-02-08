import requests

url = "https://discord.com/api/webhooks/1468583296668536832/7Gnry05SP7XXaZnI4T63pWbX8TxfJ3ABhvhZN9rQ3vrZ4LEF-QSo0sSRtPbl-zK_-qdu"

print("Testing webhook...")
response = requests.post(url, json={"content": "Test from Python"})

print(f"Status Code: {response.status_code}")
if response.status_code == 204:
    print("[OK] Webhook is working!")
elif response.status_code == 404:
    print("[ERROR] Webhook not found (404) - it may have been deleted")
    print("Please create a new webhook in Discord")
else:
    print(f"[ERROR] Unexpected response: {response.text}")

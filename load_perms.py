import subprocess
import time

def run_js(code):
    clean = code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
    apple = f'tell application "Safari" to tell document 1 to do JavaScript "{clean}"'
    res = subprocess.run(["osascript", "-e", apple], capture_output=True, text=True)
    return res.stdout.strip()

print("1. Permissions qo'shish...")
# Graph API Explorer da Permissions maydoniga ruxsatlar qo'shamiz
perms = [
    "pages_show_list",
    "pages_read_engagement", 
    "pages_manage_metadata",
    "instagram_basic",
    "instagram_manage_comments",
    "instagram_manage_messages"
]

# Graph API Explorer URL ga to'g'ridan-to'g'ri scope parametrlarini berib o'tish mumkin!
scope_param = "%2C".join(perms)
explorer_url = f"https://developers.facebook.com/tools/explorer/?app_id=1985009042456329&scope={scope_param}"
print("Explorer URL with scopes:", explorer_url)

cmd = f'tell application "Safari" to set URL of document 1 to "{explorer_url}"'
subprocess.run(["osascript", "-e", cmd])

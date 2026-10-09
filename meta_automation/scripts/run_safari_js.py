import sys
import subprocess

def run_js(code, window_idx=1, tab_idx=1):
    escaped_code = code.replace('\\', '\\\\').replace('"', '\\"').replace('\r\n', ' ').replace('\n', ' ')
    apple_script = f'''tell application "Safari"
        tell tab {tab_idx} of window {window_idx}
            do JavaScript "{escaped_code}"
        end tell
    end tell'''
    res = subprocess.run(['osascript', '-e', apple_script], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"ERROR: {res.stderr}", file=sys.stderr)
        return ""
    return res.stdout.strip()

if __name__ == '__main__':
    win = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    tab = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    js = sys.stdin.read()
    output = run_js(js, win, tab)
    print(output)

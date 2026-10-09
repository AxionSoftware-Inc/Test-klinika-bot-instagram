import sys
import time
import subprocess

def copy_to_clipboard(text):
    p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    p.communicate(text.encode("utf-8"))

def run_js(code):
    escaped = code.replace('\\', '\\\\').replace('"', '\\"')
    ascript = f'''tell application "Safari"
        tell tab 1 of window 1
            do JavaScript "{escaped}"
        end tell
    end tell'''
    res = subprocess.run(['osascript', '-e', ascript], capture_output=True, text=True)
    return res.stdout.strip()

def activate_safari():
    subprocess.run(['osascript', '-e', 'tell application "Safari" to activate'])

def paste_clipboard():
    subprocess.run(['osascript', '-e', '''tell application "System Events"
        keystroke "a" using {command down}
        delay 0.1
        keystroke "v" using {command down}
    end tell'''])

def set_question(idx, title, answer):
    print(f"Setting Question {idx+1}...")
    # 1. Scroll and focus input
    res = run_js(f'''(() => {{
        const inputs = Array.from(document.querySelectorAll('input[type="text"]'));
        if (!inputs[{idx}]) return "Input not found";
        inputs[{idx}].scrollIntoView({{ behavior: "smooth", block: "center" }});
        inputs[{idx}].focus();
        inputs[{idx}].select();
        return "Focused input";
    }})()''')
    print("Input focus result:", res)
    time.sleep(0.3)
    
    copy_to_clipboard(title)
    activate_safari()
    time.sleep(0.2)
    paste_clipboard()
    time.sleep(0.3)

    # 2. Scroll and focus textbox
    res = run_js(f'''(() => {{
        const boxes = Array.from(document.querySelectorAll('div[role="textbox"]'));
        if (!boxes[{idx}]) return "Box not found";
        boxes[{idx}].scrollIntoView({{ behavior: "smooth", block: "center" }});
        boxes[{idx}].focus();
        return "Focused box";
    }})()''')
    print("Box focus result:", res)
    time.sleep(0.3)

    copy_to_clipboard(answer)
    activate_safari()
    time.sleep(0.2)
    paste_clipboard()
    time.sleep(0.3)
    print(f"Question {idx+1} set successfully!")

if __name__ == '__main__':
    idx = int(sys.argv[1])
    title = sys.argv[2]
    with open(sys.argv[3], 'r', encoding='utf-8') as f:
        answer = f.read()
    set_question(idx, title, answer)

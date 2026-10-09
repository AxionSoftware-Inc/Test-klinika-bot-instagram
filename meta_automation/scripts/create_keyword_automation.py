import sys
import time
import subprocess

def copy_to_clipboard(text):
    p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    p.communicate(text.encode("utf-8"))

def run_js(code):
    escaped = code.replace('\\', '\\\\').replace('"', '\\"').replace('\r\n', ' ').replace('\n', ' ')
    ascript = f'''tell application "Safari"
        tell tab 1 of window 1
            do JavaScript "{escaped}"
        end tell
    end tell'''
    res = subprocess.run(['osascript', '-e', ascript], capture_output=True, text=True)
    return res.stdout.strip()

def activate_safari():
    subprocess.run(['osascript', '-e', 'tell application "Safari" to activate'])

def wait_for_form():
    print("Waiting for form to hydrate...")
    for _ in range(20):
        c = run_js('document.querySelectorAll("input").length')
        try:
            if float(c) >= 5:
                print("Form ready! Inputs count:", c)
                return True
        except:
            pass
        time.sleep(0.5)
    print("Form wait timeout!")
    return False

def create_keyword_automation(name, keywords, message):
    if not wait_for_form():
        sys.exit(1)

    print(f"Creating automation: {name}...")
    
    # 1. Turn ON toggle (inputs[0])
    run_js('''(() => {
        const toggle = document.querySelectorAll('input')[0];
        if (toggle && !toggle.checked) toggle.click();
    })()''')
    time.sleep(0.4)

    # 2. Set Name (inputs[1])
    run_js('''(() => {
        const nameInput = document.querySelectorAll('input')[1];
        if (nameInput) {
            nameInput.focus();
            nameInput.select();
        }
    })()''')
    copy_to_clipboard(name)
    activate_safari()
    time.sleep(0.2)
    subprocess.run(['osascript', '-e', '''tell application "System Events"
        keystroke "a" using {command down}
        delay 0.1
        keystroke "v" using {command down}
    end tell'''])
    time.sleep(0.4)

    # 3. Check Messenger and Instagram checkboxes (inputs[2] and inputs[3])
    run_js('''(() => {
        const cbMessenger = document.querySelectorAll('input')[2];
        const cbInstagram = document.querySelectorAll('input')[3];
        if (cbMessenger && !cbMessenger.checked) cbMessenger.click();
        if (cbInstagram && !cbInstagram.checked) cbInstagram.click();
    })()''')
    time.sleep(0.4)

    # 4. Add keywords using inputs[4]
    for kw in keywords:
        print(f"Adding keyword: {kw}")
        run_js('''(() => {
            const kwInput = document.querySelectorAll('input')[4];
            if (kwInput) kwInput.focus();
        })()''')
        activate_safari()
        time.sleep(0.2)
        escaped_kw = kw.replace('"', '\\"')
        subprocess.run(['osascript', '-e', f'''tell application "System Events"
            keystroke "{escaped_kw}"
            delay 0.1
            key code 36
        end tell'''])
        time.sleep(0.4)

    # 5. Set message
    print("Setting message text...")
    copy_to_clipboard(message)
    run_js('''(() => {
        const box = document.querySelector('div[role="textbox"]');
        if (box) {
            box.scrollIntoView({ behavior: "smooth", block: "center" });
            box.focus();
        }
    })()''')
    activate_safari()
    time.sleep(0.3)
    subprocess.run(['osascript', '-e', '''tell application "System Events"
        keystroke "a" using {command down}
        delay 0.1
        keystroke "v" using {command down}
    end tell'''])
    time.sleep(0.5)

    # 6. Click Save changes
    print("Clicking Save changes...")
    res = run_js('''(() => {
        const btn = Array.from(document.querySelectorAll('button, div[role="button"]'))
            .find(b => b.innerText && b.innerText.trim() === 'Save changes');
        if (btn) {
            btn.click();
            return "Saved";
        }
        return "Save button not found";
    })()''')
    print("Save result:", res)
    
    # Wait for save to complete
    time.sleep(3)
    print(f"Automation '{name}' completed!")

if __name__ == '__main__':
    name = sys.argv[1]
    with open(sys.argv[2], 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    with open(sys.argv[3], 'r', encoding='utf-8') as f:
        message = f.read()
    create_keyword_automation(name, keywords, message)

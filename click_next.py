import subprocess
import time

def run_js(code):
    code_clean = code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
    applescript = f'''
    tell application "Safari"
        tell document 1
            do JavaScript "{code_clean}"
        end tell
    end tell
    '''
    res = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
    return res.stdout.strip()

print("Next tugmasini bosish...")
run_js("""
let all = Array.from(document.querySelectorAll('*'));
let nextBtn = all.reverse().find(el => el.textContent && el.textContent.trim() === 'Next');
if (nextBtn) {
    let opts = { bubbles: true, cancelable: true, view: window };
    nextBtn.dispatchEvent(new MouseEvent('mousedown', opts));
    nextBtn.dispatchEvent(new MouseEvent('mouseup', opts));
    nextBtn.dispatchEvent(new MouseEvent('click', opts));
}
""")

time.sleep(2)
txt = run_js("document.body.innerText.substring(0, 300);")
print("Keyingi sahifa:", txt)

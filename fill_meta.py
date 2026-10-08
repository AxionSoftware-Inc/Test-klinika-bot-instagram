import subprocess
import time

def run_js(code):
    # Qo'shtirnoqlarni tozalash
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

print("Formani topish va to'ldirish...")
run_js("""
let labels = Array.from(document.querySelectorAll('label, div, span'));
let nameLabel = labels.find(l => l.textContent && l.textContent.trim() === 'App name');
if (nameLabel) {
    let parent = nameLabel.closest('div');
    while (parent && !parent.querySelector('input')) {
        parent = parent.parentElement;
    }
    if (parent) {
        let inp = parent.querySelector('input');
        if (inp) {
            inp.focus();
            let last = inp.value;
            inp.value = 'Klinika Automation';
            let tracker = inp._valueTracker;
            if (tracker) tracker.setValue(last);
            inp.dispatchEvent(new Event('input', { bubbles: true }));
            inp.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
}
""")

time.sleep(1)

# Next bosish
run_js("""
let all = Array.from(document.querySelectorAll('*'));
let nextBtn = all.reverse().find(el => el.textContent && el.textContent.trim() === 'Next');
if (nextBtn) {
    nextBtn.focus();
    nextBtn.click();
}
""")

time.sleep(2)
txt = run_js("document.body.innerText.substring(0, 300);")
print("Natija:", txt)

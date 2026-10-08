import subprocess

def run_js(code):
    clean = code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
    apple = f'tell application "Safari" to tell document 1 to do JavaScript "{clean}"'
    res = subprocess.run(["osascript", "-e", apple], capture_output=True, text=True)
    return res.stdout.strip()

js = """
(() => {
    let res = [];
    let all = Array.from(document.querySelectorAll('*'));
    for (let el of all) {
        let t = el.innerText ? el.innerText.trim() : '';
        if (t.includes('Business messaging (3)') || t === 'Add' || t === 'Next') {
            let r = el.getBoundingClientRect();
            if (r.width > 0 && r.height > 0) {
                res.push(t.substring(0, 25) + ' -> ' + Math.round(r.left + r.width/2) + ',' + Math.round(r.top + r.height/2));
            }
        }
    }
    return res.join(' | ');
})()
"""

print("Natija:", run_js(js))

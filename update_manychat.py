import subprocess
import time

def run_js(code):
    clean = code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
    apple = f'tell application "Safari" to tell document 1 to do JavaScript "{clean}"'
    res = subprocess.run(["osascript", "-e", apple], capture_output=True, text=True)
    return res.stdout.strip()

print("1. Keywords to'ldirish...")
js_keywords = """
(() => {
    let inputs = Array.from(document.querySelectorAll('input, textarea'));
    for (let inp of inputs) {
        if (inp.placeholder && inp.placeholder.toLowerCase().includes('price') || inp.value.includes('narxi')) {
            inp.value = '+, narxi, info, salom, assalomu alaykum, qayerda, qabul, 1, klinika';
            inp.dispatchEvent(new Event('input', { bubbles: true }));
            inp.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
})()
"""
run_js(js_keywords)
time.sleep(1)

print("2. Linkni yangilash...")
js_link = """
(() => {
    let inputs = Array.from(document.querySelectorAll('input'));
    for (let inp of inputs) {
        if (inp.value && inp.value.includes('t.me')) {
            inp.value = 'https://t.me/klinikatesttt_bot?start=insta';
            inp.dispatchEvent(new Event('input', { bubbles: true }));
            inp.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
})()
"""
run_js(js_link)
time.sleep(1)

print("3. Go Live bosish...")
from precise_click import click_at
# Go Live koordinatasi (yuqori o'ng burchak yoki o'ng panelda)
js_golive = """
(() => {
    let all = Array.from(document.querySelectorAll('*'));
    let btn = all.find(e => e.innerText && (e.innerText.trim() === 'Go Live' || e.innerText.trim() === 'Set Live' || e.innerText.trim() === 'Save'));
    if (btn) {
        let r = btn.getBoundingClientRect();
        return Math.round(r.left + r.width/2) + ',' + Math.round(r.top + r.height/2);
    }
    return 'none';
})()
"""
gl_coords = run_js(js_golive)
print("Go Live coords:", gl_coords)
if gl_coords and gl_coords != 'none':
    p = [int(v) for v in gl_coords.split(',')]
    click_at(p[0], p[1] + 85)
    time.sleep(2)

print("Holat:", run_js("(() => document.body.innerText.substring(0, 300))()"))

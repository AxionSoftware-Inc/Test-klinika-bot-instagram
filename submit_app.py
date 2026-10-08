from precise_click import click_at
from get_coords import run_js
import time
import subprocess

# Pastga scroll qilish
run_js("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(1)

# Yangi koordinatalarni olamiz
js_create = """
(() => {
    let all = Array.from(document.querySelectorAll('*'));
    let btn = all.find(e => e.innerText && e.innerText.trim() === 'Create app');
    if (btn) {
        let r = btn.getBoundingClientRect();
        return Math.round(r.left + r.width/2) + ',' + Math.round(r.top + r.height/2);
    }
    return 'none';
})()
"""
coords = run_js(js_create)
print("Scroll qilingandan keyingi Create app koordinatasi:", coords)

if coords and coords != 'none':
    parts = [int(p) for p in coords.split(',')]
    click_at(parts[0], parts[1] + 85)
    time.sleep(2)

# Agar parol so'ralsa
print("Parol tekshirilmoqda...")
run_js("""
let pwd = document.querySelector('input[type="password"]');
if (pwd) {
    pwd.value = 'a7161062';
    pwd.dispatchEvent(new Event('input', { bubbles: true }));
    pwd.dispatchEvent(new Event('change', { bubbles: true }));
    let submitBtn = Array.from(document.querySelectorAll('*')).reverse().find(e => e.innerText && (e.innerText.trim() === 'Submit' || e.innerText.trim() === 'Continue'));
    if (submitBtn) submitBtn.click();
}
""")

time.sleep(3)
print("Hozirgi URL:", run_js("(() => window.location.href)()"))

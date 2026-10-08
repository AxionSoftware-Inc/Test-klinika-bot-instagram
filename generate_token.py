from precise_click import click_at
from get_coords import run_js
import time

print("1. 'Add a Permission' bosilmoqda...")
js_perm = """
(() => {
    let all = Array.from(document.querySelectorAll('*'));
    let btn = all.find(e => e.innerText && e.innerText.trim() === 'Add a Permission');
    if (btn) {
        let r = btn.getBoundingClientRect();
        return Math.round(r.left + r.width/2) + ',' + Math.round(r.top + r.height/2);
    }
    return 'none';
})()
"""
pos_perm = run_js(js_perm)
print("Permission coords:", pos_perm)
if pos_perm and pos_perm != 'none':
    p = [int(v) for v in pos_perm.split(',')]
    click_at(p[0], p[1] + 85)
    time.sleep(1)

# Generate Access Token bosamiz
print("2. 'Generate Access Token' bosilmoqda...")
js_gen = """
(() => {
    let all = Array.from(document.querySelectorAll('*'));
    let btn = all.find(e => e.innerText && e.innerText.trim() === 'Generate Access Token');
    if (btn) {
        let r = btn.getBoundingClientRect();
        return Math.round(r.left + r.width/2) + ',' + Math.round(r.top + r.height/2);
    }
    return 'none';
})()
"""
pos_gen = run_js(js_gen)
print("Gen token coords:", pos_gen)
if pos_gen and pos_gen != 'none':
    p = [int(v) for v in pos_gen.split(',')]
    click_at(p[0], p[1] + 85)
    time.sleep(2)

print("Hozirgi holat:")
print(run_js("(() => document.body.innerText.substring(0, 400))()"))

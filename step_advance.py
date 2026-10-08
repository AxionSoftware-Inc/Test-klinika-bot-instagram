from precise_click import click_at
from get_coords import run_js
import time

print("1. Business messaging bosilmoqda (533, 527)...")
click_at(533, 527)
time.sleep(1.5)

# Chiqqan Add tugmalarining koordinatalarini olamiz
js_add = """
(() => {
    let res = [];
    let all = Array.from(document.querySelectorAll('*'));
    for (let el of all) {
        let t = el.innerText ? el.innerText.trim() : '';
        if (t === 'Add' || t === 'Select') {
            let r = el.getBoundingClientRect();
            if (r.width > 0 && r.height > 0) {
                res.push(Math.round(r.left + r.width/2) + ',' + Math.round(r.top + r.height/2));
            }
        }
    }
    return res.join(' | ');
})()
"""
add_res = run_js(js_add)
print("Add koordinatalari:", add_res)

if add_res:
    for coord in add_res.split(' | '):
        parts = [int(p) for p in coord.split(',')]
        ax, ay = parts[0], parts[1] + 85
        print(f"Add bosilmoqda: ({ax}, {ay})")
        click_at(ax, ay)
        time.sleep(0.5)

time.sleep(1)

# Next bosamiz
print("Next bosilmoqda (1350, 933)...")
click_at(1350, 933)
time.sleep(2)

print("Yangi sahifa holati:")
print(run_js("(() => document.body.innerText.substring(0, 300))()"))

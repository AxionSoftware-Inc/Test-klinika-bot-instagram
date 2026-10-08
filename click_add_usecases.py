from precise_click import click_at
from get_coords import run_js
import time

print("Add use cases tugmasi koordinatasi olinmoqda...")
js = """
(() => {
    let all = Array.from(document.querySelectorAll('*'));
    let btn = all.find(e => e.innerText && e.innerText.trim() === 'Add use cases');
    if (btn) {
        let r = btn.getBoundingClientRect();
        return Math.round(r.left + r.width/2) + ',' + Math.round(r.top + r.height/2);
    }
    return 'none';
})()
"""
coords = run_js(js)
print("Add use cases coords:", coords)
if coords and coords != 'none':
    p = [int(v) for v in coords.split(',')]
    click_at(p[0], p[1] + 85)
    time.sleep(2)

print("Hozirgi holat:")
print(run_js("(() => document.body.innerText.substring(0, 400))()"))

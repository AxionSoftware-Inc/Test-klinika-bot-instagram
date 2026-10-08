from get_coords import run_js
from precise_click import click_at
import time

# Kartochka ichidagi tugma yoki kartochkaning o'zini bosamiz
js_card = """
(() => {
    let all = Array.from(document.querySelectorAll('*'));
    let card = all.find(e => e.innerText && e.innerText.includes('Engage with customers on Messenger'));
    if (card) {
        let r = card.getBoundingClientRect();
        return Math.round(r.left + r.width/2) + ',' + Math.round(r.top + r.height/2);
    }
    return 'none';
})()
"""
coords = run_js(js_card)
print("Kartochka koordinatasi:", coords)

if coords and coords != 'none':
    parts = [int(p) for p in coords.split(',')]
    cx, cy = parts[0], parts[1] + 85
    print(f"Kartochka bosilmoqda: ({cx}, {cy})")
    click_at(cx, cy)
    time.sleep(1)

# Next bosish: Next koordinatasi (1350, 920 + 85 = 1005 yoki 933)
print("Next bosilmoqda...")
click_at(1350, 1005)
time.sleep(0.5)
click_at(1350, 933)
time.sleep(2)

print("Keyingi sahifa:")
print(run_js("(() => document.body.innerText.substring(0, 300))()"))

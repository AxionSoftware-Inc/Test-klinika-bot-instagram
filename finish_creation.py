from precise_click import click_at
from get_coords import run_js
import time

def get_element_pos(text_match):
    js = f"""
    (() => {{
        let all = Array.from(document.querySelectorAll('*'));
        let el = all.find(e => e.innerText && e.innerText.trim().startsWith('{text_match}'));
        if (el) {{
            let r = el.getBoundingClientRect();
            return Math.round(r.left + r.width/2) + ',' + Math.round(r.top + r.height/2);
        }}
        return 'none';
    }})()
    """
    res = run_js(js)
    if res and res != 'none':
        parts = [int(p) for p in res.split(',')]
        return parts[0], parts[1] + 85
    return None

print("1. 'I don’t want to connect' tanlanmoqda...")
pos = get_element_pos("I don’t want to connect")
if pos:
    print(f"Tanlanmoqda: {pos}")
    click_at(pos[0], pos[1])
    time.sleep(1)

print("2. Next bosilmoqda...")
pos_next = get_element_pos("Next")
if pos_next:
    print(f"Next: {pos_next}")
    click_at(pos_next[0], pos_next[1])
    time.sleep(2)

print("3. Requirements sahifasida Next bosilmoqda...")
pos_next2 = get_element_pos("Next")
if pos_next2:
    print(f"Next 2: {pos_next2}")
    click_at(pos_next2[0], pos_next2[1])
    time.sleep(2)

print("4. Overview sahifasida Create app bosilmoqda...")
pos_create = get_element_pos("Create app")
if pos_create:
    print(f"Create app: {pos_create}")
    click_at(pos_create[0], pos_create[1])
    time.sleep(3)

print("YAKUNIY SAHIFA:")
print(run_js("(() => document.body.innerText.substring(0, 300))()"))

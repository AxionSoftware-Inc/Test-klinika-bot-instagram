import ctypes
import ctypes.util
import time
import subprocess
import json

cg = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreGraphics"))

class CGPoint(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

cg.CGEventCreateMouseEvent.restype = ctypes.c_void_p
cg.CGEventCreateMouseEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32, CGPoint, ctypes.c_uint32]
cg.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]

kCGEventLeftMouseDown = 1
kCGEventLeftMouseUp = 2
kCGHIDEventTap = 0

def click_screen(x, y):
    point = CGPoint(x, y)
    down = cg.CGEventCreateMouseEvent(None, kCGEventLeftMouseDown, point, 0)
    up = cg.CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, point, 0)
    cg.CGEventPost(kCGHIDEventTap, down)
    time.sleep(0.05)
    cg.CGEventPost(kCGHIDEventTap, up)

def run_js(code):
    clean = code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
    apple = f'tell application "Safari" to tell document 1 to do JavaScript "{clean}"'
    res = subprocess.run(["osascript", "-e", apple], capture_output=True, text=True)
    return res.stdout.strip()

def click_element_text(text_match):
    js = f'''
    let all = Array.from(document.querySelectorAll('*'));
    let el = all.find(e => e.textContent && e.textContent.trim().startsWith('{text_match}'));
    if (el) {{
        let r = el.getBoundingClientRect();
        Math.round(r.left + r.width/2) + ',' + Math.round(r.top + r.height/2);
    }} else 'none';
    '''
    coords = run_js(js)
    if coords and coords != 'none':
        parts = [int(p) for p in coords.split(',')]
        # Safari toolbar offset ~85px
        sx, sy = parts[0], parts[1] + 85
        print(f"Bosilmoqda: '{text_match}' -> ({sx}, {sy})")
        click_screen(sx, sy)
        return True
    return False

# 1. Business messaging bosamiz
print("1. Business messaging tanlanmoqda...")
click_element_text("Business messaging")
time.sleep(1)

# 2. Add tugmasini topib bosamiz
print("2. Add bosilmoqda...")
js_add = '''
let all = Array.from(document.querySelectorAll('*'));
let el = all.find(e => e.textContent && (e.textContent.trim() === 'Add' || e.textContent.trim() === 'Select'));
if (el) {
    let r = el.getBoundingClientRect();
    Math.round(r.left + r.width/2) + ',' + Math.round(r.top + r.height/2);
} else 'none';
'''
add_coords = run_js(js_add)
if add_coords and add_coords != 'none':
    parts = [int(p) for p in add_coords.split(',')]
    click_screen(parts[0], parts[1] + 85)
time.sleep(1)

# 3. Next bosamiz
print("3. Next bosilmoqda...")
click_element_text("Next")
time.sleep(2)

print("Hozirgi sahifa:")
print(run_js("document.body.innerText.substring(0, 300);"))

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

def click_at(x, y):
    point = CGPoint(x, y)
    down = cg.CGEventCreateMouseEvent(None, kCGEventLeftMouseDown, point, 0)
    up = cg.CGEventCreateMouseEvent(None, kCGEventLeftMouseUp, point, 0)
    cg.CGEventPost(kCGHIDEventTap, down)
    time.sleep(0.05)
    cg.CGEventPost(kCGHIDEventTap, up)

# Next tugmasining Safari ichidagi aniq koordinatasini topamiz
find_js = '''
tell application "Safari"
    activate
    tell document 1
        do JavaScript "
            let all = Array.from(document.querySelectorAll('*'));
            let btn = all.reverse().find(el => el.textContent && el.textContent.trim() === 'Next');
            if (btn) {
                let r = btn.getBoundingClientRect();
                window.screenX + ',' + window.screenY + ',' + Math.round(r.left + r.width/2) + ',' + Math.round(r.top + r.height/2);
            } else {
                'none';
            }
        "
    end tell
end tell
'''
res = subprocess.run(["osascript", "-e", find_js], capture_output=True, text=True).stdout.strip()
print("JS Koordinatalari:", res)

# Safari oynasining o'lchamini olamiz
win_res = subprocess.run(["osascript", "-e", 'tell application "Safari" to return bounds of window 1'], capture_output=True, text=True).stdout.strip()
bounds = [int(v.strip()) for v in win_res.split(",")]
print("Window bounds:", bounds)

# Ko'p hollarda macOS Safari toolbar balandligi 85-90px bo'ladi
# Ekranning o'ng tomonidagi Next tugmasiga bosish:
# Turli ehtimoliy Y nuqtalariga bosib ko'ramiz
for y_offset in [800, 850, 900, 950]:
    target_x = bounds[0] + int((bounds[2] - bounds[0]) * 0.72)
    target_y = bounds[1] + y_offset
    print(f"Sinov bosish: ({target_x}, {target_y})")
    click_at(target_x, target_y)
    time.sleep(0.3)

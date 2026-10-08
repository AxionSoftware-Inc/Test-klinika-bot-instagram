import ctypes
import ctypes.util
import time
import subprocess

# macOS CoreGraphics C-kutubxonasini yuklash
cg = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreGraphics"))

# CGPoint tuzilmasi
class CGPoint(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

# C funksiyalari
cg.CGEventCreateMouseEvent.restype = ctypes.c_void_p
cg.CGEventCreateMouseEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32, CGPoint, ctypes.c_uint32]
cg.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]

# Event turlari
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

# 1. Safari oynasining joylashuvini olamiz
applescript = '''
tell application "Safari"
    activate
    set b to bounds of window 1
    return (item 1 of b as string) & "," & (item 2 of b as string) & "," & (item 3 of b as string) & "," & (item 4 of b as string)
end tell
'''
res = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
bounds = [int(v.strip()) for v in res.stdout.strip().split(",")]
win_x, win_y, win_w, win_h = bounds[0], bounds[1], bounds[2] - bounds[0], bounds[3] - bounds[1]
print(f"Safari oynasi: {win_x}, {win_y}, o'lchami: {win_w}x{win_h}")

# Next tugmasi oynaning o'ng pastki qismida bo'ladi (taxminan x: 75-85%, y: 80-90%)
target_x = win_x + int(win_w * 0.78)
target_y = win_y + int(win_h * 0.85)
print(f"Haqiqiy apparat sichqoncha bosilmoqda: ({target_x}, {target_y})")

click_at(target_x, target_y)
time.sleep(1)

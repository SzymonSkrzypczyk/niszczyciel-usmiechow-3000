import ctypes
from ctypes import wintypes
import csv
import os
import threading
from time import time_ns
import platform
from pynput import keyboard, mouse

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
OUTFILE = "events.csv"
LOCK = threading.Lock()
# first Q then Ctrl to stop
STOP_COMBO = {keyboard.Key.ctrl_l, keyboard.KeyCode.from_char('q')}
# current combination of pressed keys
current_keys = set()

if not os.path.exists(OUTFILE) or os.stat(OUTFILE).st_size == 0:
    with open(OUTFILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ts_ns",
            "event_type",
            "key_or_buttonq",
            "x", "y",
            "scroll_dx", "scroll_dy",
            "focused_window"
        ])


def get_active_window_title():
    if platform.system() != "Windows":
        return ""

    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi

        hwnd = user32.GetForegroundWindow()
        if hwnd == 0:
            return ""

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        process_handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
        if not process_handle:
            return ""

        exe_name = ctypes.create_unicode_buffer(260)
        if psapi.GetModuleFileNameExW(process_handle, None, exe_name, 260) == 0:
            kernel32.CloseHandle(process_handle)
            return ""

        kernel32.CloseHandle(process_handle)
        return exe_name.value.split("\\")[-1]
    except Exception:
        return ""


def write_row(row):
    with LOCK:
        with open(OUTFILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)


def on_press(key):
    current_keys.add(key)

    if STOP_COMBO.issubset(current_keys):
        stop_all_listeners()
    try:
        k = key.char  # single-char keys
    except AttributeError:
        k = str(key)  # special keys

    ts = time_ns()
    focused = get_active_window_title()
    write_row([ts, "key_down", k, "", "", "", "", focused])


def on_release(key):
    if key in current_keys:
        current_keys.remove(key)

    try:
        k = key.char
    except AttributeError:
        k = str(key)

    ts = time_ns()
    focused = get_active_window_title()
    write_row([ts, "key_up", k, "", "", "", "", focused])

def on_move(x, y):
    ts = time_ns()
    focused = get_active_window_title()
    write_row([ts, "mouse_move", "", x, y, "", "", focused])

def on_click(x, y, button, pressed):
    ts = time_ns()
    focused = get_active_window_title()
    etype = "mouse_click_down" if pressed else "mouse_click_up"
    write_row([ts, etype, str(button), x, y, "", "", focused])

def on_scroll(x, y, dx, dy):
    ts = time_ns()
    focused = get_active_window_title()
    write_row([ts, "mouse_scroll", "", x, y, dx, dy, focused])

kbd_listener = None
mouse_listener = None

def stop_all_listeners():
    # Stop both listeners (called when Esc is released)
    if mouse_listener and mouse_listener.running:
        mouse_listener.stop()
    if kbd_listener and kbd_listener.running:
        kbd_listener.stop()

def main():
    global kbd_listener, mouse_listener

    mouse_listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll
    )
    mouse_listener.start()

    kbd_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )
    kbd_listener.start()

    kbd_listener.join()
    mouse_listener.join()

if __name__ == "__main__":
    main()

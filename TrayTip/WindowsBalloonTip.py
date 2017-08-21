# The WindowsBalloonTip class comes from this stackoverflow post:
# https://stackoverflow.com/a/17262942/6692652

from win32api import *
from win32gui import *
import win32con
import sys, os
import struct
import time

# Class
class WindowsBalloonTip:
    def __init__(self, title, msg, iconPathName=None):
        message_map = { win32con.WM_DESTROY: self.OnDestroy,}

        # Register the window class.
        wc = WNDCLASS()
        hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = 'PythonTaskbar'
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        classAtom = RegisterClass(wc)

        # Create the window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = CreateWindow(classAtom, "Taskbar", style, 0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0, hinst, None)
        UpdateWindow(self.hwnd)

        # Icons managment
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
            if iconPathName:
                hicon = LoadImage(hinst, 0, win32con.IMAGE_ICON, 0, 0, icon_flags)
            else:
                hicon = CreateIconFromResource(LoadResource(None, win32con.RT_ICON, 1), True)
        except:
            hicon = LoadIcon(0, win32con.IDI_APPLICATION)
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, 'Tooltip')

        # Notify
        dwInfoFlags = 0x24 # NIIF_USER|NIIF_LARGE_ICON - not defined in win32con?
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, (self.hwnd, 0, NIF_INFO, win32con.WM_USER+20, hicon, 'Balloon Tooltip', msg, 200, title, dwInfoFlags))
        # self.show_balloon(title, msg)
        time.sleep(5)

        # Destroy
        DestroyWindow(self.hwnd)
        classAtom = UnregisterClass(classAtom, hinst)
    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        Shell_NotifyIcon(NIM_DELETE, nid)
        PostQuitMessage(0) # Terminate the app.


# Main
if __name__ == '__main__':
    # Example
    WindowsBalloonTip('Lorem Ipsum', 'Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit...')
    WindowsBalloonTip('Example two', 'There is no one who loves pain itself, who seeks after it and wants to have it, simply because it is pain...')

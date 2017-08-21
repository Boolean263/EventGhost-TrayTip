# -*- coding: utf-8 -*-

import eg

eg.RegisterPlugin(
    name = "TrayTip",
    author = "David Perry <d.perry@utoronto.ca>",
    version = "0.0.1",
    kind = "other",
    description = "Show notices in the system tray.",
    url = "https://github.com/Boolean263/EventGhost-TrayTip",
    guid = "{707e86ff-660f-49cd-a00a-9963a7351df0}",
)

import wx
import win32api
import win32gui
import win32con
import winerror
import sys, os

class TrayTip(eg.PluginBase):
    payloads = {}

    def __init__(self):
        self.AddAction(showTip)

    def __start__(self):
        # Register the window class.
        wc = win32gui.WNDCLASS()
        self.hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = 'EventGhostTrayTip'
        wc.lpfnWndProc = {
            win32con.WM_DESTROY: self.OnDestroy,
            win32con.WM_USER+20: self.OnNotify,
        }
        self.classAtom = win32gui.RegisterClass(wc)

    def __stop__(self):
        self.classAtom = win32gui.UnregisterClass(self.classAtom, self.hinst)

    def setPayload(self, hwnd, payload=None):
        self.payloads[hwnd] = payload

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        del self.payloads[hwnd]

    def OnNotify(self, hwnd, msg, wparam, lparam):
        #eg.PrintNotice("Notify: msg={:08X} wparam={:08X} lparam={:08X}".format(msg, wparam, lparam))
        # Magic numbers until I learn their proper constant names:
        # 0x0402: seems to mean the appearance of the notification
        # 0x0404: the notification vanishes (on its own?)
        # 0x0405: disappeared by click
        if lparam == 0x0405:
            try:
                payload = self.payloads[hwnd]
            except KeyError:
                payload = None
            eg.TriggerEvent("Clicked", payload=payload, prefix='TrayTip')
        if lparam == 0x0404 or lparam == 0x0405:
            win32gui.DestroyWindow(hwnd)

class showTip(eg.ActionBase):
    name = "Show system tray message"
    description = "Shows a message in the Windows Action Center."

    def __call__(self, title="", msg="", payload=None):
        title = eg.ParseString(title or "EventGhost")
        msg = eg.ParseString(msg or "This is a notification from EventGhost.")
        if payload:
            payload = eg.ParseString(payload)

        # https://stackoverflow.com/a/17262942/6692652
        # Create the window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        hwnd = win32gui.CreateWindow(self.plugin.classAtom, "Taskbar", style, 0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0, self.plugin.hinst, None)
        win32gui.UpdateWindow(hwnd)
        self.plugin.setPayload(hwnd, payload)

        # Icons managment
        iconPathName = None # for now
        try:
            if iconPathName:
                icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                hicon = win32gui.LoadImage(self.plugin.hinst, 0, win32con.IMAGE_ICON, 0, 0, icon_flags)
            else:
                hicon = win32gui.CreateIconFromResource(win32api.LoadResource(None, win32con.RT_ICON, 1), True)
        except:
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (hwnd, 0, flags, win32con.WM_USER+20, hicon, 'Tooltip')

        # Notify
        dwInfoFlags = 0x24 # NIIF_USER|NIIF_LARGE_ICON - not defined in win32con?
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, (hwnd, 0, win32gui.NIF_INFO, win32con.WM_USER+20, hicon, 'Balloon Tooltip', msg, 200, title, dwInfoFlags))

        # Window destruction is taken care of in the parent class

    def GetLabel(self, title, msg, payload):
        return "\"{}\" ({}) {}".format(title, msg, repr(payload))

    def Configure(self, title="", msg="", payload=""):
        panel = eg.ConfigPanel(self)
        titleCtrl = panel.TextCtrl(title)
        msgCtrl = panel.TextCtrl(msg)
        payloadCtrl = panel.TextCtrl(payload)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel.StaticText("Title"))
        sizer.Add(titleCtrl, 0, wx.EXPAND|wx.TOP)
        sizer.Add(panel.StaticText("Message"))
        sizer.Add(msgCtrl, 0, wx.EXPAND|wx.TOP)
        sizer.Add(panel.StaticText("Event payload if clicked (optional)"))
        sizer.Add(payloadCtrl, 0, wx.EXPAND|wx.TOP)

        panel.sizer.Add(sizer, 0, wx.EXPAND|wx.ALL, 10)

        while panel.Affirmed():
            panel.SetResult(
                titleCtrl.GetValue(),
                msgCtrl.GetValue(),
                payloadCtrl.GetValue(),
            )


#
# Editor modelines  -  https://www.wireshark.org/tools/modelines.html
#
# Local variables:
# c-basic-offset: 4
# tab-width: 4
# indent-tabs-mode: nil
# coding: utf-8
# End:
#
# vi: set shiftwidth=4 tabstop=4 expandtab fileencoding=utf-8:
# :indentSize=4:tabSize=4:noTabs=true:coding=utf-8:
#

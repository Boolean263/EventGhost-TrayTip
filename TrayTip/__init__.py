# -*- coding: utf-8 -*-
#
# This file is part of EventGhost.
# Copyright © 2005-2016 EventGhost Project <http://www.eventghost.org/>
#
# EventGhost is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# EventGhost is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with EventGhost. If not, see <http://www.gnu.org/licenses/>.

import eg


eg.RegisterPlugin(
    name="TrayTip",
    author=(
        "David Perry <d.perry@utoronto.ca>",
        "kdschlosser",
    ),
    version="0.1.0",
    kind="other",
    description="Show notices in the system tray.",
    url="https://github.com/Boolean263/EventGhost-TrayTip",
    guid="{707E86FF-660F-49CD-A00A-9963A7351DF0}",
)

import wx # NOQA
import win32api # NOQA
import win32gui # NOQA
import win32con # NOQA
import winerror # NOQA
import sys # NOQA
import os # NOQA
import ctypes # NOQA

# Windows constants
WM_TRAYICON = win32con.WM_USER + 20
NIN_BALLOONSHOW = win32con.WM_USER + 2
NIN_BALLOONHIDE = win32con.WM_USER + 3
NIN_BALLOONTIMEOUT = win32con.WM_USER + 4
NIN_BALLOONUSERCLICK = win32con.WM_USER + 5
NIIF_NONE = 0x00
NIIF_INFO = 0x01
NIIF_WARNING = 0x02
NIIF_ERROR = 0x03
NIIF_USER = 0x04
NIIF_NOSOUND = 0x10
NIIF_LARGE_ICON = 0x20
NIIF_RESPECT_QUIET_TIME = 0x80

class Text(eg.TranslatableStrings):
    class ShowTip:
        name = "Show system tray message"
        description = "Shows a message in the Windows Action Center."
        title_lbl = "Title"
        message_lbl = "Message"
        payload_lbl = "Event payload (optional)"
        iconOpt_lbl = "Icon"
        sound_lbl = "Play Sound"

class TrayTip(eg.PluginBase):
    text = Text
    payloads = {}

    def __init__(self):
        self.info.eventPrefix = 'TrayTip'
        self.AddAction(ShowTip)

    def __start__(self):
        # Register the window class.
        wc = win32gui.WNDCLASS()
        self.hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = 'EventGhostTrayTip'
        wc.lpfnWndProc = {
            win32con.WM_DESTROY: self.OnDestroy,
            WM_TRAYICON: self.OnNotify,
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

    def OnNotify(self, hwnd, msg, wParam, lParam):
        # eg.PrintNotice("Notify: msg={:08X} wparam={:08X} lparam={:08X}"
        # .format(msg, wparam, lparam))

        if msg == WM_TRAYICON:
            if hwnd in self.payloads:
                payload = self.payloads[hwnd]
            else:
                payload = None

            if lParam == NIN_BALLOONSHOW:
                self.TriggerEvent("Show", payload=payload)

            elif lParam == NIN_BALLOONHIDE:
                self.TriggerEvent("Hide", payload=payload)

            elif lParam == NIN_BALLOONTIMEOUT:
                self.TriggerEvent("TimedOut", payload=payload)
                win32gui.DestroyWindow(hwnd)

            elif lParam == NIN_BALLOONUSERCLICK:
                self.TriggerEvent("Clicked", payload=payload)
                win32gui.DestroyWindow(hwnd)

class ShowTip(eg.ActionBase):
    iconOpts = ("None", "Info", "Warning", "Error", "EventGhost", "Custom")
    # Since I hate magic constants
    ICON_NONE, ICON_INFO, ICON_WARNING, ICON_ERROR, ICON_EG, ICON_CUSTOM = range(len(iconOpts))

    def __call__(self, title="", msg="", payload=None, iconOpt=ICON_EG, sound=True):
        if iconOpt is None:
            iconOpt = self.ICON_EG
        title = eg.ParseString(title or "EventGhost")
        msg = eg.ParseString(msg or "This is a notification from EventGhost.")
        if payload and isinstance(payload, basestring):
            payload = eg.ParseString(payload)

        # https://stackoverflow.com/a/17262942/6692652
        # Create the window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        hwnd = win32gui.CreateWindow(
            self.plugin.classAtom,
            "TaskBar",
            style,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            self.plugin.hinst,
            None
        )
        win32gui.UpdateWindow(hwnd)
        self.plugin.setPayload(hwnd, payload)

        # Icons management
        # Default to no icon if something goes weird
        hicon = None
        dwInfoFlags = 0x00
        try:
            if iconOpt == self.ICON_INFO:
                dwInfoFlags = NIIF_INFO|NIIF_LARGE_ICON
            elif iconOpt == self.ICON_WARNING:
                dwInfoFlags = NIIF_WARNING|NIIF_LARGE_ICON
            elif iconOpt == self.ICON_ERROR:
                dwInfoFlags = NIIF_ERROR|NIIF_LARGE_ICON
            elif iconOpt == self.ICON_EG:
                # Get the first icon from the EventGhost executable
                hicon = win32gui.CreateIconFromResource(
                    win32api.LoadResource(None, win32con.RT_ICON, 1),
                    True
                )
                dwInfoFlags = NIIF_USER|NIIF_LARGE_ICON
            elif isinstance(iconOpt, basestring):
                filename, idx = iconOpt.split(";", 1)
                lib = win32api.LoadLibrary(filename)
                hicon = win32gui.LoadIcon(lib, int(idx)+1)
                dwInfoFlags = NIIF_USER|NIIF_LARGE_ICON
                win32api.FreeLibrary(lib)
        except Exception as ex:
            eg.PrintError(str(ex))
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        if not sound:
            dwInfoFlags |= NIIF_NOSOUND
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (hwnd, 0, flags, WM_TRAYICON, hicon, 'Tooltip')

        # Notify
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        win32gui.Shell_NotifyIcon(
            win32gui.NIM_MODIFY,
            (
                hwnd,
                0,
                win32gui.NIF_INFO,
                WM_TRAYICON,
                hicon,
                'Balloon Tooltip',
                msg,
                200,
                title,
                dwInfoFlags
            )
        )

        # Window destruction is taken care of in the parent class

    def GetLabel(self, title, msg, payload, iconOpt=None, sound=True):
        return "\"{}\" ({}) {}".format(title, msg, repr(payload))

    def Configure(self, title="", msg="", payload="", iconOpt=ICON_EG, sound=True):
        text = self.text
        panel = eg.ConfigPanel(self)

        # Use a global to work around issues with closures in 2.x
        global _traytip_iconFile
        _traytip_iconFile = [ os.path.join(eg.mainDir, "EventGhost.exe"), 0 ]
        if isinstance(iconOpt, basestring):
            _traytip_iconFile = list(iconOpt.split(";",1))
            _traytip_iconFile[1] = int(_traytip_iconFile[1])
            iconOpt = self.ICON_CUSTOM

        title_st = panel.StaticText(text.title_lbl)
        title_ctrl = panel.TextCtrl(title)
        msg_st = panel.StaticText(text.message_lbl)
        msg_ctrl = panel.TextCtrl(msg)
        payload_st = panel.StaticText(text.payload_lbl)
        payload_ctrl = panel.TextCtrl(payload)
        iconOpt_st = panel.StaticText(text.iconOpt_lbl)
        iconOpt_ctrl = panel.Choice(iconOpt, choices=self.iconOpts)
        sound_ctrl = panel.CheckBox(sound, text.sound_lbl)
        iconPath_ctrl = panel.Button(label="", size=wx.Size(32,32), style=wx.BU_NOTEXT)

        # It's a bit ugly IMHO to close around the above controls
        # with function definitions like this. But it works, at least for now.
        def updateIconPath():
            icon = wx.IconFromLocation(wx.IconLocation(*_traytip_iconFile))
            iconPath_ctrl.SetBitmap(wx.BitmapFromIcon(icon))
        def onIconPath(event):
            iconOpt_ctrl.SetValue(self.ICON_CUSTOM)
            global _traytip_iconFile
            # This is the part that fails if _traytip_iconFile isn't global
            _traytip_iconFile = list( pickIcon(*_traytip_iconFile) )
            updateIconPath()
        def onIconOpt(event):
            if event.GetInt() == self.ICON_CUSTOM:
                onIconPath(None)

        iconPath_ctrl.Bind(wx.EVT_BUTTON, onIconPath)
        iconOpt_ctrl.Bind(wx.EVT_CHOICE, onIconOpt)
        updateIconPath()

        eg.EqualizeWidths((title_st, msg_st, payload_st, iconOpt_st))
        eg.EqualizeWidths((title_ctrl, msg_ctrl, payload_ctrl))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(iconOpt_st, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(iconOpt_ctrl, 0, wx.ALL, 5)
        sizer.Add(iconPath_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        panel.sizer.Add(sizer, 0, wx.EXPAND)

        for (st, ctrl) in (
                (title_st, title_ctrl),
                (msg_st, msg_ctrl),
                (payload_st, payload_ctrl),
        ):
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(st, 0, wx.EXPAND | wx.ALL, 5)
            sizer.Add(ctrl, 0, wx.EXPAND | wx.ALL, 5)
            panel.sizer.Add(sizer, 0, wx.EXPAND)

        panel.sizer.Add(sound_ctrl)

        while panel.Affirmed():
            if iconOpt_ctrl.GetValue() != self.ICON_CUSTOM:
                newicon = iconOpt_ctrl.GetValue()
            else:
                newicon = ";".join(str(x) for x in _traytip_iconFile)
            panel.SetResult(
                title_ctrl.GetValue(),
                msg_ctrl.GetValue(),
                payload_ctrl.GetValue(),
                newicon,
                sound_ctrl.GetValue(),
            )
        del _traytip_iconFile

def pickIcon(filename, index=0):
    PickIconDlg = ctypes.windll.shell32.PickIconDlg
    PickIconDlg.argtypes = [
            ctypes.wintypes.HWND,
            ctypes.c_wchar_p,
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_uint)
    ]
    c_fn = ctypes.c_wchar_p(filename)
    c_ix = ctypes.c_uint(index)

    # If the user picks something, c_fn and c_ix change;
    # if not, they don't
    PickIconDlg(None, c_fn, win32con.MAX_PATH, c_ix)
    return c_fn.value, c_ix.value

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

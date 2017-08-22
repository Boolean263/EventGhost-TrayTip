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
    author="David Perry <d.perry@utoronto.ca>",
    version="0.0.1",
    kind="other",
    description="Show notices in the system tray.",
    url="https://github.com/Boolean263/EventGhost-TrayTip",
    guid="{707e86ff-660f-49cd-a00a-9963a7351df0}",
)

import wx # NOQA
import win32api # NOQA
import win32gui # NOQA
import win32con # NOQA
import winerror # NOQA
import sys # NOQA
import os # NOQA


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
            win32con.WM_USER + 20: self.OnNotify,
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
        # eg.PrintNotice("Notify: msg={:08X} wparam={:08X} lparam={:08X}"
        # .format(msg, wparam, lparam))
        # Magic numbers until I learn their proper constant names:
        # 0x0402: seems to mean the appearance of the notification
        # 0x0404: the notification vanishes (on its own?)
        # 0x0405: disappeared by click

        if lparam in (0x0404, 0x0405):
            if lparam == 0x0405:
                try:
                    payload = self.payloads[hwnd]
                except KeyError:
                    payload = None
                eg.TriggerEvent("Clicked", payload=payload, prefix='TrayTip')

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
        iconPathName = None # for now
        try:
            if iconPathName:
                icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
                hicon = win32gui.LoadImage(
                    self.plugin.hinst,
                    0,
                    win32con.IMAGE_ICON,
                    0,
                    0,
                    icon_flags
                )
            else:
                hicon = win32gui.CreateIconFromResource(
                    win32api.LoadResource(None, win32con.RT_ICON, 1), True)
        except:
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (hwnd, 0, flags, win32con.WM_USER + 20, hicon, 'Tooltip')

        # Notify
        # NIIF_USER|NIIF_LARGE_ICON - not defined in win32con?
        dwInfoFlags = 0x24
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        win32gui.Shell_NotifyIcon(
            win32gui.NIM_MODIFY,
            (
                hwnd,
                0,
                win32gui.NIF_INFO,
                win32con.WM_USER + 20,
                hicon,
                'Balloon Tooltip',
                msg,
                200,
                title,
                dwInfoFlags
            )
        )

        # Window destruction is taken care of in the parent class

    def GetLabel(self, title, msg, payload):
        return "\"{}\" ({}) {}".format(title, msg, repr(payload))

    def Configure(self, title="", msg="", payload=""):
        panel = eg.ConfigPanel(self)

        title_st = panel.StaticText("Title:")
        title_ctrl = panel.TextCtrl(title)
        msg_st = panel.StaticText("Message:")
        msg_ctrl = panel.TextCtrl(msg)
        payload_st = panel.StaticText("Event payload if clicked (optional):")
        payload_ctrl = panel.TextCtrl(payload)

        eg.EqualizeWidths((title_st, msg_st, payload_st))
        eg.EqualizeWidths((title_ctrl, msg_ctrl, payload_ctrl))

        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_sizer.Add(title_st, 0, wx.EXPAND | wx.ALL, 5)
        title_sizer.Add(title_ctrl, 0, wx.EXPAND | wx.ALL, 5)

        msg_sizer = wx.BoxSizer(wx.HORIZONTAL)
        msg_sizer.Add(msg_st, 0, wx.EXPAND | wx.ALL, 5)
        msg_sizer.Add(msg_ctrl, 0, wx.EXPAND | wx.ALL, 5)

        payload_sizer = wx.BoxSizer(wx.HORIZONTAL)
        payload_sizer.Add(payload_st, 0, wx.EXPAND | wx.ALL, 5)
        payload_sizer.Add(payload_ctrl, 0, wx.EXPAND | wx.ALL, 5)

        panel.sizer.Add(title_sizer, 0, wx.EXPAND)
        panel.sizer.Add(msg_sizer, 0, wx.EXPAND)
        panel.sizer.Add(payload_sizer, 0, wx.EXPAND)

        # Optionally you can do this as well for adding the controls.
        # I like it when it is keyed out. less "voodooish" code that way
        # but it all depends on your liking.
        #
        # def add(*args):
        #     for st, ctrl in args:
        #         sizer = wx.BoxSizer(wx.HORIZONTAL)
        #         sizer.Add(st, 0, wx.EXPAND | wx.ALL, 5)
        #         sizer.Add(ctrl, 0, wx.EXPAND | wx.ALL, 5)
        #         panel.sizer.Add(sizer, 0, wx.EXPAND)
        #
        # add(
        #     (title_st, title_ctrl),
        #     (msg_st, msg_ctrl),
        #     (payload_st, payload_ctrl)
        # )

        while panel.Affirmed():
            panel.SetResult(
                title_ctrl.GetValue(),
                msg_ctrl.GetValue(),
                payload_ctrl.GetValue(),
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

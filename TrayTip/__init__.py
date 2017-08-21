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

# The WindowsBalloonTip class comes from this stackoverflow post:
# https://stackoverflow.com/a/17262942/6692652
from .WindowsBalloonTip import WindowsBalloonTip

from threading import Thread
import wx
import sys
import os.path

class TrayTip(eg.PluginBase):

    def __init__(self):
        self.AddAction(showTip)

class showTip(eg.ActionBase):
    name = "Show system message"
    description = "Shows a message in the Windows Action Center."

    def __call__(self, title="", msg="", icon=None):
        title = eg.ParseString(title)
        msg = eg.ParseString(msg)

        # EventGhost freezes if we call WindowsBallonTip directly.
        # Is it bad that we never join() this thread?
        Thread(target=WindowsBalloonTip, args=(title, msg, icon)).start()

    def GetLabel(self, title, msg):
        return "{}: {}".format(title, msg)

    def Configure(self, title="", msg=""):
        panel = eg.ConfigPanel(self)
        titleCtrl = panel.TextCtrl(title)
        msgCtrl = panel.TextCtrl(msg)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel.StaticText("Title"))
        sizer.Add(titleCtrl, 0, wx.EXPAND|wx.TOP)
        sizer.Add(panel.StaticText("Message"))
        sizer.Add(msgCtrl, 0, wx.EXPAND|wx.TOP)

        panel.sizer.Add(sizer, 0, wx.EXPAND|wx.ALL, 10)

        while panel.Affirmed():
            panel.SetResult(
                titleCtrl.GetValue(),
                msgCtrl.GetValue(),
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

#
# TileCutter debugger window
#
# Use:
# from debug import DebugFrame as debug
# To import previously intialised global debug() method, for use with debug output in any module that
# requires it
#

import wx

class DebugFrame(wx.Frame):
    """Debugging output display, debug.out() (or just debug()) to output debugging text"""
    init = True
    def __init__(self, parentOrLine, id=wx.ID_ANY, title="", debug_on=True):
        """Debug init method overloaded, if it hasn't been initialised before, then requires
           all parameters, and returns a reference to this debug object, otherwise requires
           only the first parameter (the line to output) and uses out() method (like __call__)"""
        if DebugFrame.init:
            DebugFrame.init = False
            # Init text and counter
            DebugFrame.text = ""
            DebugFrame.count = 0
            DebugFrame.debug_on = debug_on
            # Frame init
            wx.Frame.__init__(self, parentOrLine, wx.ID_ANY, title, (0,0), (600,300), style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
            DebugFrame.panel = wx.Panel(self, wx.ID_ANY)
            DebugFrame.sizer = wx.BoxSizer(wx.VERTICAL)
            DebugFrame.textbox = wx.TextCtrl(DebugFrame.panel, wx.ID_ANY, DebugFrame.text, (-1,-1), (-1,-1), wx.TE_MULTILINE|wx.TE_READONLY)
            DebugFrame.sizer.Add(DebugFrame.textbox, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
            #Layout sizers
            DebugFrame.panel.SetSizer(DebugFrame.sizer)
            DebugFrame.panel.SetAutoLayout(1)
            DebugFrame.panel.Layout()
        else:
            self.out(parentOrLine)
    def out(self, line):
        """Writes a line of debugging information to the window"""
        if DebugFrame.debug_on:
            DebugFrame.count += 1
            t = "[%s] %s\n" % (DebugFrame.count, line)
            DebugFrame.text = DebugFrame.text + t
            DebugFrame.textbox.SetValue(DebugFrame.text)
            DebugFrame.textbox.ShowPosition(len(DebugFrame.text))
    def __call__(self, line):
        """Calls the out() function"""
        if DebugFrame.debug_on:
            self.out(line)



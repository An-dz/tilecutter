# coding: UTF-8
#
# TileCutter debugger window
#
# Use:
# from debug import DebugFrame as debug
# To import previously intialised global debug() method, for use with debug output in any module that
# requires it
#

import StringIO
import sys, os

import config
config = config.Config()

from datetime import datetime as dt

class Log(object):
    """Debug/log output to file"""
    file = None
    stringio = None
    line_number = 0
    def __init__(self):
        """"""
        if Log.file == None:
            # Appends this session's log info to the logging file
            Log.file = open(config.logfile, "a")
            # Stores this session's log info in memory for view in the built-in debug window
            Log.stringio = StringIO.StringIO()
    def __call__(self, s):
        """Calls self.write()"""
        self.write(s)
    def out(self, s):
        """Proxy of write"""
        self.write(s)
    def write(self, s):
        """Write a string to file"""
        # Could be improved by splitting input string by newlines and writing an output line
        # for every part, prevent double newlines, prettier format for errors etc.
        # Only one timestamp for errors though
        line_number += 1
        # Prepend current time/date, append newline
        outline = dt.now().replace(microsecond=0).isoformat(" ") + " | " + s + "\n"
        Log.file.write(outline)
        Log.file.flush()
        # Prepend line number, append newline
        outline = "[%s] %s\n" % (line_number, s)
        Log.stringio.write(outline)
        Log.stringio.flush()


import wx


# Make debug() seperate from debug frame, debugger a file like object/StringIO that can be written to
# DebugFrame updated via this file like object, optional, can be inited after the debugger is
# Ideally debugger inited as early in program as possible, before anything else

# Debugger extends StringIO, adding line numbering etc.
# Debug window displays output (like tail)

import sched, time

class DebugFrame(wx.Frame):
    """Debugging output display, shows contents of log in-program"""
    def __init__(self, parent, log, id=wx.ID_ANY, title=""):
        """"""
        # Init text and counter
        self.log = log
        self.count = 0
        self.timer = sched.scheduler(time.time, time.sleep)
        # Frame init
        wx.Frame.__init__(self, parent, id, title, (0,0), (600,300), style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.textbox = wx.TextCtrl(self.panel, wx.ID_ANY, self.log.getvalue(), (-1,-1), (-1,-1), wx.TE_MULTILINE|wx.TE_READONLY)
        self.sizer.Add(self.textbox, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
        #Layout sizers
        self.panel.SetSizer(self.sizer)
        self.panel.SetAutoLayout(1)
        self.panel.Layout()
    def update(self):
        """Update the log window, calls itself every second"""
        self.textbox.SetValue(self.log.getvalue())
        self.textbox.ShowPosition(len(self.text))
        self.timer.enter(1, 1, self.update, ())
        
##class DebugFrame(wx.Frame):
##    """Debugging output display, debug.out() (or just debug()) to output debugging text"""
##    init = True
##    def __init__(self, parentOrLine, id=wx.ID_ANY, title="", debug_on=True):
##        """Debug init method overloaded, if it hasn't been initialised before, then requires
##           all parameters, and returns a reference to this debug object, otherwise requires
##           only the first parameter (the line to output) and uses out() method (like __call__)"""
##        if DebugFrame.init:
##            DebugFrame.init = False
##            # Init text and counter
##            DebugFrame.text = ""
##            DebugFrame.count = 0
##            DebugFrame.debug_on = debug_on
##            # Frame init
##            wx.Frame.__init__(self, parentOrLine, wx.ID_ANY, title, (0,0), (600,300), style=wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL)
##            DebugFrame.panel = wx.Panel(self, wx.ID_ANY)
##            DebugFrame.sizer = wx.BoxSizer(wx.VERTICAL)
##            DebugFrame.textbox = wx.TextCtrl(DebugFrame.panel, wx.ID_ANY, DebugFrame.text, (-1,-1), (-1,-1), wx.TE_MULTILINE|wx.TE_READONLY)
##            DebugFrame.sizer.Add(DebugFrame.textbox, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
##            #Layout sizers
##            DebugFrame.panel.SetSizer(DebugFrame.sizer)
##            DebugFrame.panel.SetAutoLayout(1)
##            DebugFrame.panel.Layout()
##        else:
##            self.out(parentOrLine)
##    def out(self, line):
##        """Writes a line of debugging information to the window"""
##        if DebugFrame.debug_on:
##            DebugFrame.count += 1
##            t = "[%s] %s\n" % (DebugFrame.count, line)
##            DebugFrame.text = DebugFrame.text + t
##            DebugFrame.textbox.SetValue(DebugFrame.text)
##            DebugFrame.textbox.ShowPosition(len(DebugFrame.text))
##    def __call__(self, line):
##        """Calls the out() function"""
##        if DebugFrame.debug_on:
##            self.out(line)



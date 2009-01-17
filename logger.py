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
            Log.stringio = StringIO.StringIO("some text")
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
        self.line_number += 1
        # Prepend current time/date, append newline
        outline = dt.now().replace(microsecond=0).isoformat(" ") + " |    " + s + "\n"
        Log.file.write(outline)
        Log.file.flush()
        # Prepend line number, append newline
        outline = "[%s] %s\n" % (self.line_number, s)
        Log.stringio.write(outline)
        Log.stringio.flush()


# coding: UTF-8
#
# TileCutter debugger window
#

# Copyright � 2008-2010 Timothy Baldock. All Rights Reserved.

# To use:
# import logger
# debug = logger.Log()
#
# Then debug(<string to output>)
# Time/newline added automatically

import config
config = config.Config()

from datetime import datetime as datetime

import codecs

class Log(object):
    """Debug/log output to file"""
    file = None
    def __init__(self, file=None):
        """"""
        if Log.file == None:
            if file == None:
                # Appends this session's log info to the logging file
                Log.file = codecs.open(config.logfile, "a", "UTF-8")
            else:
                Log.file = codecs.open(file, "a", "UTF-8")
    def __call__(self, s):
        """Calls self.write()"""
        self.out(s)
    def out(self, s):
        """Write a string to file, stripping newlines and reformatting"""
        s = s.replace(u"\r", u"")
        splits = s.split(u"\n")
        writedate = True
        for k in splits:
            outline = datetime.now().replace(microsecond=0).isoformat(" ") + " | " + k + "\n"
            Log.file.write(outline, date=writedate)
            writedate = False
        Log.file.flush()
    def write(self, s, date=False):
        """Write a string to file, preserving newlines fed in"""
        # Check string, if it's entirely whitespace or just a newline, or blank do nothing
        # Prepend current time/date, append newline
        dt = datetime.now().replace(microsecond=0).isoformat(" ")
        # Check if next line will need the date prepending
        if date:
            outline = dt + u" | " + s
        else:
            outline = u" " * len(dt) + u" | " + s
        Log.file.write(outline)
        Log.file.flush()


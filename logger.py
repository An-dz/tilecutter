# coding: UTF-8
#
# Logger - logging utility
#

# Copyright © 2008-2011 Timothy Baldock. All Rights Reserved.

# To use:
# import logger
# debug = logger.Log()
#
# Then debug(<string to output>)
# Time/newline added automatically

import sys, os

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
                # Default for config is to specify log file as platform_default
                if config.logfile == "platform_default":
                    if sys.platform == "darwin":
                        file = os.path.expanduser(u"~/Library/Logs/tilecutter.log")
                    elif sys.platform == "win32":
                        file = os.path.normpath(os.path.expanduser(u"~/Application Data/tilecutter/tilecutter.log"))

                    else:
                        file = os.path.expanduser(u"~/.tilecutter/tilecutter.log")
                else:
                    # Appends this session's log info to the logging file
                    file = config.logfile

            # Confirm if path exists, create directories if needed
            if not os.path.isdir(os.path.split(file)[0]):
                os.makedirs(os.path.split(file)[0])

            Log.file = codecs.open(file, "a", "UTF-8")

    def __call__(self, s):
        """Calls self.write()"""
        self.out(s)
    def out(self, s):
        """Write a string to file, stripping newlines and reformatting"""
        # If it's a unicode string don't convert it
        if type(s) != type(u""):
            s = unicode(s, "UTF-8")
            s = u"Converted to unicode:\n" + s
        s = s.replace(u"\r", u"")
        splits = s.split(u"\n")
        writedate = True
        for k in splits:
            outline = k + "\n"
            self.write(outline, date=writedate)
            writedate = False
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
        # Check last character of line is a newline
        if outline[-1] != u"\n":
            outline = outline + u"\n"
        Log.file.write(outline)
        Log.file.flush()


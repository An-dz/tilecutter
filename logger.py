# coding: UTF-8
#
# TileCutter debugger window
#

# To use:
# import logger
# debug = logger.Log()
#
# Then debug(<string to output>)
# Time/newline added automatically

import config
config = config.Config()

from datetime import datetime as dt

class Log(object):
    """Debug/log output to file"""
    file = None
    line_number = 0
    def __init__(self):
        """"""
        if Log.file == None:
            # Appends this session's log info to the logging file
            Log.file = open(config.logfile, "a")
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


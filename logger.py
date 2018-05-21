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

import sys, os, codecs
from datetime import datetime as datetime

from environment import getenvvar

import config
config = config.Config()

class Log(object):
    """Debug/log output to file"""
    file = None
    def platform_default_log_location(self):
        """Returns default log file location for the platform we are running on"""
        if sys.platform == "darwin":
            file = os.path.expanduser("~/Library/Logs/tilecutter.log")
            source = "darwin"
        elif sys.platform == "win32":
            file = os.path.join(getenvvar("APPDATA"), "tilecutter\\tilecutter.log")
            #file = os.path.normpath(os.path.expanduser("~/Application Data/tilecutter/tilecutter.log"))
            #file = unicode(file, sys.getfilesystemencoding())
            source = "win32"
        else:
            file = os.path.expanduser("~/.tilecutter/tilecutter.log")
            source = "unix"
        return file, source
    def __init__(self, file=None):
        """"""
        if Log.file == None:
            source = "args"
            if file == None:
                # Default for config is to specify log file as blank and logfile_platform_default as True
                if config.logfile_platform_default:
                    file, source = self.platform_default_log_location()
                else:
                    # Appends this session's log info to the logging file
                    file = os.path.abspath(config.logfile)
                    source = "config"
            # Confirm if path exists, create directories if needed
            if not os.path.isdir(os.path.split(file)[0]):
                os.makedirs(os.path.split(file)[0])

            Log.file = codecs.open(file, "a", "UTF-8")
            # First time logger is initialised write something useful to the start of the log
            self.out("-----------------------------------------------------------------------------------------\nLogger opened file (%s) from source: %s" % (file, source))

    # Default debug level for statements without a level specified is 1, which will appear on all debug levels except off
    def __call__(self, s, level=1):
        """This allows the logger object to be called directly"""
        self.out(s, level)

    def out(self, s, level=1):
        """Write a string to file, stripping newlines and reformatting"""
        # If currently configured debug level is less than debug level of this statement, do nothing
        if config.debug_level < level:
            return False
        s = s.replace("\r", "")
        splits = s.split("\n")
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
            outline = dt + " | " + s
        else:
            outline = " " * len(dt) + " | " + s
        # Check last character of line is a newline
        if outline[-1] != "\n":
            outline = outline + "\n"
        Log.file.write(outline)
        Log.file.flush()


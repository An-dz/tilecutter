# coding: UTF-8
#
# Config Management Utility Script
#

import sys, os
import copy, math

from debug import DebugFrame as debug

# This class will provide a wrapper to the ConfigParser built in class
# This file should also define hard-coded defaults for all settings, lest the config file
# go missing...

class Config:
    """Program configuration object"""
    config = {}
    def __init__(self):
        """"""
        # First time Config is intialised call the read_in function to init all the settings
        # from file. Subsequent instances of Config all refer to the same in-memory copy of
        # the settings, can add a setting by name, set a setting's value, remove a setting
        # re-read settings from file etc.
    def read(self, filename):
        """"""
    def write(self, filename):
        """"""
    
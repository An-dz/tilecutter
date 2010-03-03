# coding: UTF-8
#
# Config Management Utility
#

# Copyright © 2008-2010 Timothy Baldock. All Rights Reserved.

##import simplejson as json
import json

# Better to use json module in python 2.6 here
# Tuples probably need to be converted to arrays here

class Config(object):
    """Program configuration object"""
    # The first time this object is instantiated, config is populated
    config = {}
    # All externally settable variables must be included in defaults, or they won't be read
    # by Config on loading. Non-externally settable variables can be placed in internals
    # Internals will always be checked before config
    defaults = {
        "debug_on": True,
        "logfile": "tilecutter.log",
        "transparent": [231,255,255],
        "default_paksize": 64,
##        "PROJECT_FILE_EXTENSION": ".tcp",
        "valid_image_extensions": [".png"],
        "OFFSET_NEGATIVE_ALLOWED": False,
        "window_size": [-1,-1],
        "window_position": [-1,-1],

        "last_save_path": "",

        "negative_offset_allowed": False,
        "default_image_path": "test.png",

        "path_to_makeobj": "makeobj",
        "write_dat": True,

        "choicelist_paksize": [16,32,48,64,80,96,112,128,144,160,176,192,208,224,240],
        "choicelist_views": [1,2,4],
        "choicelist_dims": [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
        "choicelist_dims_z": [1,2,3,4],
        "default_language": "english_translation",
        }
    internals = {
        "version": "0.5.5",
        }
    conf_path = "tc.config"

    def __init__(self):
        """"""
        # First time Config is intialised call the read_in function to init all the settings
        # from file. Subsequent instances of Config all refer to the same in-memory copy of
        # the settings, can add a setting by name, set a setting's value, remove a setting
        # re-read settings from file etc.
        if Config.config == {}:
            try:
                f = open(self.conf_path, "r")
                file_config = json.loads(f.read())
                f.close()
            except IOError:
                # If unable to open config file, abort and use defaults
                file_config = {}
            # Now merge this into the defaults, value from default is always overrided if there
            # is a value in the file, also means only keys with a default set are loaded in
            for k in Config.defaults.keys():
                if file_config.has_key(k):
                    Config.config[k] = file_config.pop(k)
                else:
                    Config.config[k] = Config.defaults[k]
    def __str__(self):
        """Return a string representing this object"""
        return unicode(Config.config)
    def __getattr__(self, name):
        """Lookup method by . access e.g. z = x.y"""
        if Config.internals.has_key(name):
            return Config.internals[name]
        elif Config.config.has_key(name):
            return Config.config[name]
        else:
            raise AttributeError(name)
    def __setattr__(self, name, value):
        """Set method by . access e.g. x.y = z"""
        # Internal attributes are immutable
        if name in Config.internals:
            pass
        elif name in Config.defaults:
            Config.config[name] = value
            self.save()
        else:
            object.__setattr__(self, name, value)
    def __getitem__(self, key):
        """Lookup method by dict access e.g. z = x["y"]"""
        if Config.internals.has_key(key):
            return Config.internals[key]
        elif Config.config.has_key(key):
            return Config.config[key]
        else:
            raise KeyError(key)
    def __setitem__(self, key, value):
        """Set method by dict access e.g. x["y"] = z"""
        # Again, internals are immutable
        if Config.internals.has_key(name):
            pass
        elif Config.defaults.has_key(key):
            Config.config[key] = value
            self.save()
        else:
            raise KeyError(key)
    def save(self):
        """Save the current config out to the config file"""
        f = open(self.conf_path, "w")
        f.write(json.dumps(Config.config, sort_keys=True, indent=4))
        f.close()







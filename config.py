# coding: UTF-8
#
# Config Management Utility

import codecs, json, os, sys
from environment import getenvvar

# Tuples probably need to be converted to arrays here

class Config(object):
    """Program configuration object"""
    # The first time this object is instantiated, config is populated
    config = {}

    # If a tc.config or tilecutter.config file exists in the program directory use that to load config from 
    # (to permit setting of global config, or for backwards compatibility with existing installs)
    if os.path.isfile("tc.config"):
        main_path = os.path.abspath(".")
        logs_path = os.path.join(main_path, "tilecutter.log")
        conf_path = os.path.join(main_path, "tc.config")
        source = "legacy: tc.config in program directory"
    else:
        if os.path.isfile("tilecutter.config"):
            main_path = os.path.abspath(".")
            source = "override: tilecutter.config in program directory"
        elif sys.platform == "win32":
            main_path = os.path.join(getenvvar("APPDATA"), "tilecutter\\")
            source = "win32 auto location"
        else:
            main_path = os.path.expanduser("~/.tilecutter/")
            source = "unix auto location"

        conf_path = os.path.join(main_path, "tilecutter.config")
        logs_path = os.path.join(main_path, "tilecutter.log")

        if sys.platform == "darwin":
            logs_path = os.path.expanduser("~/Library/Logs/tilecutter.log")
            source = "darwin auto location"

    # All externally settable variables must be included in defaults, or they won't be read
    # by Config on loading. Non-externally settable variables can be placed in internals
    # Internals will always be checked before config
    defaults = {
        "debug_on": True,
        "debug_level": 2,
        "logfile": logs_path,
        "logfile_platform_default": True,
        "transparent":     [231, 255, 255],
        "transparent_bg": [[153, 153, 153], [103, 103, 103]],
        "default_paksize": 64,
        "valid_image_extensions": [".png"],
        "OFFSET_NEGATIVE_ALLOWED": False,
        "window_size":     [-1, -1],
        "window_position": [-1, -1],
        "window_maximised": False,

        "last_save_path": "",
        "last_image_path": "",

        "negative_offset_allowed": False,
        "default_image_path": "",

        "path_to_makeobj": "",
        "write_dat": True,

        "default_language": "English",
    }
    internals = {
        "version": "1.0.0",
        "choicelist_paksize": [16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240],
        "choicelist_views":  [1, 2, 4],
        "choicelist_dims":   [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        "choicelist_dims_z": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    }

    def __init__(self):
        """First time Config is intialised, call the read_in function to init all the settings
        from file. Subsequent instances of Config all refer to the same in-memory copy of
        the settings, can add a setting by name, set a setting's value, remove a setting
        re-read settings from file etc."""
        if Config.config == {}:
            try:
                f = codecs.open(self.conf_path, "r", "UTF-8")
                file_config = json.loads(f.read())
                f.close()
            except IOError:
                # If unable to open config file, abort and use defaults
                file_config = {}
            # Now merge this into the defaults, value from default is always overrided if there
            # is a value in the file, also means only keys with a default set are loaded in
            for k in list(Config.defaults.keys()):
                if k in file_config:
                    Config.config[k] = file_config.pop(k)
                else:
                    Config.config[k] = Config.defaults[k]

    def __str__(self):
        """Return a string representing this object"""
        return str(Config.config)

    def __getattr__(self, name):
        """Lookup method by . access e.g. z = x.y"""
        if name in Config.internals:
            return Config.internals[name]
        elif name in Config.config:
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
        """Lookup method by dict access e.g. z = x['y']"""
        if key in Config.internals:
            return Config.internals[key]
        elif key in Config.config:
            return Config.config[key]
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        """Set method by dict access e.g. x['y'] = z"""
        # Again, internals are immutable
        if name in Config.internals:
            pass
        elif key in Config.defaults:
            Config.config[key] = value
            self.save()
        else:
            raise KeyError(key)

    def save(self):
        """Save the current config out to the config file"""
        # Confirm if path exists, create directories if needed
        if not os.path.isdir(os.path.split(self.conf_path)[0]):
            os.makedirs(os.path.split(self.conf_path)[0])

        try:
            f = codecs.open(self.conf_path, "w", "UTF-8")
            f.write(json.dumps(Config.config, ensure_ascii=False, sort_keys=True, indent=4))
            f.close()
        except IOError:
            debug("IOError working with file %s, likely this path doesn't exist or the user I am running as doesn't have permission to write to it" % self.conf_path)
            return False

        return True

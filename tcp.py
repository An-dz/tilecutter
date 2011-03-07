# coding: UTF-8
#
# TileCutter - .tcp file reading/writing functions
#

# Copyright © 2011 Timothy Baldock. All Rights Reserved.


import logger
debug = logger.Log()

import sys, os

import pickle
import json

import tcproject
import project

import config
config = config.Config()

class tcp_writer(object):
    """"""
    def __init__(self, filename, mode):
        """"""
        debug(u"tcp_writer: Initialising new tcp_writer, file: %s, mode: %s" % (filename, mode))

        # Confirm if path exists, create directories if needed
        if not os.path.isdir(os.path.split(filename)[0]):
            os.makedirs(os.path.split(filename)[0])

        self.filename = filename
        self.mode = mode

    def write(self, obj):
        """Write object to file, return success"""
        debug(u"tcp_writer: write - Writing object: %s to file" % str(obj))
        if self.mode == "pickle":
            debug(u"tcp_writer: write - Deprecation warning, pickle save mode no longer supported!")
            output_string = self.pickle_object(obj, 2)
        elif self.mode == "json":
            debug(u"tcp_writer: write - Preparing output in JSON format.")
            saveobj = {"type": "TCP_JSON",
                       "version": "%s" % config.version,
                       "comment": "This is a TileCutter Project file (JSON formatted). You may edit it by hand if you are careful.",
                       "data": obj.props,
                       }
            try:
                output_string = json.dumps(saveobj, ensure_ascii=False, sort_keys=True, indent=4)
            except:
                # Any problems this has probably failed, so don't write out file
                return False

        # Needs addition of exception handling for IO
        self.file = open(filename, "wb")
        self.file.write(output_string)
        self.file.close()

        return True

    def pickle_object(self, obj, picklemode = 2):
        """"""
        debug(u"pickle_object, picklemode: %s" % picklemode)
        params = obj.prep_serialise()
        pickle_string = pickle.dumps(obj, picklemode)
        obj.post_serialise(params)

        return pickle_string

class tcp_reader(object):
    """The main application, pre-window launch stuff should go here"""
    def __init__(self, filename):
        """"""
        debug(u"Initialising new tcp_reader, file: %s" % filename)
        try:
            self.file = open(filename, "rb")
        except IOError:
            debug(u"Opening file for reading failed, file probably does not exist!")
            self.file = None

    def load(self, params):
        """Load object from file, return deserialised object"""
        debug(u"Loading object from file")
        # Optional params argument which contains values which should be passed to post_serialise method of object to initalise it
        str = self.file.read()
        self.file.close()
        # Try to load file as JSON format first, if this fails try to load it as pickle
        try:
            loadobj = self.unjson_object(str, params)
            if loadobj["type"] == "TCP_JSON":
                # Init new project using loaded data from dict
                obj = project.Project(params[0], load=loadobj["data"])
            else:
                # This isn't a well-formed json tcp file, abort
                debug(u"tcp_reader: load - JSON file is not well-formed, type incorrect, aborting load")
                return False
        except ValueError:
            debug(u"tcp_reader: load - loading as JSON failed, attempting to load as pickle (legacy format)")
            try:
                legacyobj = self.unpickle_object(str, params)
            except:
                # Any error indicates failure to load, abort
                debug(u"tcp_reader: load - loading as pickle also fails, this isn't a valid .tcp file!")
                return False

        return obj

    def convert_tcproject(self, tcproj):
        """Convert an old-style tcproject object into a new style project one"""
        # tcproj represents a tcproject object
        # Frames were not implemented under this format, so assume there's only one
        # Build an input dict for a new project using the tcproject's properties
        # The validators in the project class will then take care of the rest

    def unpickle_object(self, str, params):
        """Unpickle an object from the pickled string str, call post_serialise with params"""
        debug(u"unpickle_object")
        obj = pickle.loads(str)
        obj.post_serialise(params)
        return obj

    def unjson_object(self, str, params):
        """"""
        debug(u"unjson_object")
        props_dict = json.loads(str)
        return project.Project(params[0], load=props_dict)

    def detect_filetype(self, str):
        """Detect whether data is from a json or pickle file"""
        # If first line of file reads "#TCP_JSON" then this is a json format file 
        # (should then be a comma followed by the program version that wrote it)
        if str[:9] == u"#TCP_JSON":
            return "json"
        # Otherwise it's probably either pickle format (or some trash, but the pickle decoder will find that out)
        else:
            return "pickle"


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
        debug(u"Initialising new tcp_writer, file: %s, mode: %s" % (filename, mode))

        # Confirm if path exists, create directories if needed
        if not os.path.isdir(os.path.split(filename)[0]):
            os.makedirs(os.path.split(filename)[0])

        self.file = open(filename, "wb")
        self.mode = mode

    def write(self, obj):
        """Write object to file, return success"""
        debug(u"Writing object: %s to file" % str(obj))
        if self.mode == "pickle":
            output_string = self.pickle_object(obj, 2)
        elif self.mode == "json":
            header_string = "#TCP_JSON,%s\n#This is a TileCutter Project file (JSON formatted). You may edit it by hand if you are careful and don't change anything above this line.\n" % config.version
            output_string = header_string + self.json_object(obj)

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

    def json_object(self, obj):
        """Write project object's props dict to a json formatted file"""
        debug(u"json_object")
        return json.dumps(obj.props, ensure_ascii=False, sort_keys=True, indent=4)
        

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
        # Check what kind of file it is, json or pickle
        if self.detect_filetype(str) == "pickle":
            obj = self.unpickle_object(str, params)
        elif self.detect_filetype(str) == "json":
            obj = self.unjson_object(str, params)

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


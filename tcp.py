# coding: UTF-8
#
# TileCutter - .tcp file reading/writing functions
#

# Copyright © 2011 Timothy Baldock. All Rights Reserved.


import logger
debug = logger.Log()

import sys, os

import pickle
import tcproject

#import config
#config = config.Config()
#config.save()

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
        """"""
        debug(u"json_object")

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
        # Check what kind of file it is, JSON or pickle
        if self.detect_filetype(str) == "pickle":
            obj = self.unpickle_object(str, params)
        elif self.detect_filetype(str) == "JSON":
            pass

        return obj

    def unpickle_object(self, str, params):
        """Unpickle an object from the pickled string str, call post_serialise with params"""
        debug(u"unpickle_object")
        obj = pickle.loads(str)
        obj.post_serialise(params)
        return obj

    def unjson_object(self, str):
        """"""
        debug(u"unjson_object")
        pass

    def detect_filetype(self, str):
        """Detect whether data is from a JSON or pickle file"""
        return "pickle"


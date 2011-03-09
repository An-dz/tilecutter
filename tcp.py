# coding: UTF-8
#
# TileCutter - .tcp file reading/writing functions
#

# Copyright © 2011 Timothy Baldock. All Rights Reserved.


import logger
debug = logger.Log()

import sys, os, traceback

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
                debug(u"tcp_writer: write - Error dumping json for saveobj, trace follows")
                debug(traceback.format_exc())
                # Any problems this has probably failed, so don't write out file
                return False

        # Needs addition of exception handling for IO
        try:
            f = open(self.filename, "wb")
        except IOError:
            debug(u"tcp_writer: write - IOError attempting to open file: %s for writing" % filename)
            debug(traceback.format_exc())
            return False
        try:
            f.write(output_string)
        except IOError:
            debug(u"tcp_writer: write - IOError attempting to write to file: %s" % filename)
            debug(traceback.format_exc())
            return False
        f.close()

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
        self.filename = filename

    def load(self, params):
        """Load object from file, return deserialised object"""
        debug(u"tcp_reader: load - Loading object from file")
        # Optional params argument which contains values which should be passed to post_serialise method of object to initalise it
        try:
            f = open(self.filename, "rb")
        except IOError:
            debug(u"Opening file for reading failed, file probably does not exist!")
            debug(traceback.format_exc())
        str = f.read()
        f.close()
        # Try to load file as JSON format first, if this fails try to load it as pickle
        try:
            debug(u"tcp_reader: load - attempting to load as JSON")
            loadobj = json.loads(str)
            if type(loadobj) == type({}) and loadobj.has_key("type") and loadobj["type"] == "TCP_JSON":
                debug(u"tcp_reader: load - JSON load successful, attempting to load in object")
                # Init new project using loaded data from dict
                obj = project.Project(params[0], load=loadobj["data"], save_location=self.filename, saved=True)
            else:
                # This isn't a well-formed json tcp file, abort
                debug(u"tcp_reader: load - JSON file is not well-formed, type incorrect, aborting load")
                return False
        except ValueError:
            debug(u"tcp_reader: load - loading as JSON failed, attempting to load as pickle (legacy format)")
            try:
                legacyobj = self.unpickle_object(str)
                # Build a new-style project from the old-style one
                newdict = self.convert_tcproject(legacyobj)
                obj = project.Project(params[0], load=newdict, save_location=self.filename, saved=False)
            except:
                # Any error indicates failure to load, abort
                debug(u"tcp_reader: load - loading as pickle also fails, this isn't a valid .tcp file!")
                debug(traceback.format_exc())
                return False

        return obj

    def convert_tcproject(self, tcproj):
        """Convert an old-style tcproject object into a new style project one"""
        debug(u"tcp_reader: convert_tcproject")
        # tcproj represents a tcproject object
        # Frames were not implemented under this format, so assume there's only one
        # Build an input dict for a new project using the tcproject's properties
        # The validators in the project class will then take care of the rest
        projdict = {
            # project[view][season][frame][layer][xdim][ydim][zdim]
            "dims": {
                "x": tcproj.x(),
                "y": tcproj.y(),
                "z": tcproj.z(),
                "paksize": tcproj.paksize(),
                "directions": tcproj.views(),
                "frames": 1,
                "winter": tcproj.winter(),
                "frontimage": tcproj.frontimage(),
            },
            "files": {
                "datfile_location": tcproj.datfile(),
                "datfile_write": tcproj.writedat(),
                "pngfile_location": tcproj.pngfile(),
                "pakfile_location": tcproj.pakfile(),
            },
            "dat": {
                "dat_lump": tcproj.temp_dat_properties(),
            },
        }
        viewarray = []
        for view in range(4):
            seasonarray = []
            for season in range(2):
                framearray = []
                for frame in range(1):
                    imagearray = []
                    for image in range(2):
                        imdefault = {
                            "path": tcproj[view][season][frame][image].path(),
                            "offset": tcproj[view][season][frame][image].offset,
                        }
                        imagearray.append(imdefault)
                    framearray.append(imagearray)
                seasonarray.append(framearray)
            viewarray.append(seasonarray)
        projdict["images"] = viewarray
        debug(u"tcp_reader: convert_tcproject - projdict to feed into new project is: %s" % repr(projdict))
        return projdict

    def unpickle_object(self, str, params=None):
        """Unpickle an object from the pickled string str, optionally call post_serialise with params"""
        debug(u"tcp_reader: unpickle_object - WARNING: pickle-style .tcp projects are considered a legacy format!")
        obj = pickle.loads(str)
        if params is not None:
            debug(u"tcp_reader: unpickle_object - running post_serialise")
            obj.post_serialise(params)
        debug(u"tcp_reader: unpickle_object - unpickled object: %s" % repr(obj))
        return obj


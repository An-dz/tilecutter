# TileCutter - .tcp file reading/writing functions

import logging, json, os, pickle, traceback
import config, project
config = config.Config()


class TcpWriter(object):
    """Write TCP file"""

    def __init__(self, filename, mode):
        """Initialise TCP file"""
        logging.info("TcpWriter: Initialising new TcpWriter, file: %s, mode: %s" % (filename, mode))

        # Confirm if path exists, create directories if needed
        if not os.path.isdir(os.path.split(filename)[0]):
            os.makedirs(os.path.split(filename)[0])

        self.filename = filename
        self.mode = mode

    def write(self, obj):
        """Write object to file, return success"""
        logging.info("TcpWriter: write - Writing object: %s to file" % str(obj))

        if self.mode == "pickle":
            logging.warn("TcpWriter: write - Deprecation warning, pickle save mode no longer supported!")
            output_string = self.pickle_object(obj, 2)
        elif self.mode == "json":
            logging.debug("TcpWriter: write - Preparing output in JSON format.")
            saveobj = {
                "type": "TCP_JSON",
                "version": "%s" % config.TCPversion,
                "version_tc": "%s" % config.version,
                "comment": "This is a TileCutter Project file (JSON formatted). You may edit it by hand if you are careful.",
                "data": obj.props,
            }
            try:
                output_string = json.dumps(saveobj, ensure_ascii=False, sort_keys=True, indent=4)
            except Exception:
                logging.error("TcpWriter: write - Error dumping json for saveobj, trace follows")
                logging.error(traceback.format_exc())
                # Any problems this has probably failed, so don't write out file
                return False

        # Needs addition of exception handling for IO
        try:
            f = open(self.filename, "wt")
        except IOError:
            logging.error("TcpWriter: write - IOError attempting to open file: %s for writing" % self.filename)
            logging.error(traceback.format_exc())
            return False
        try:
            f.write(output_string)
        except IOError:
            logging.error("TcpWriter: write - IOError attempting to write to file: %s" % self.filename)
            logging.error(traceback.format_exc())
            return False
        f.close()

        return True

    def pickle_object(self, obj, picklemode=2):
        """"""
        logging.info("pickle_object, picklemode: %s" % picklemode)
        params = obj.prep_serialise()
        pickle_string = pickle.dumps(obj, picklemode)
        obj.post_serialise(params)
        return pickle_string


class TcpReader(object):
    """The main application, pre-window launch stuff should go here"""

    def __init__(self, filename):
        """Get filename for other function calls"""
        logging.info("Initialising new TcpReader, file: %s" % filename)
        self.filename = filename

    def load(self, params):
        """Load object from file, return deserialised object"""
        logging.info("TcpReader: load - Loading object from file")

        # Optional params argument which contains values which should be passed to post_serialise method of object to initalise it
        try:
            f = open(self.filename, "rb")
        except IOError:
            logging.error("Opening file for reading failed, file probably does not exist!")
            logging.error(traceback.format_exc())

        file_content = f.read()
        f.close()

        # Try to load file as JSON format first, if this fails try to load it as pickle
        try:
            logging.debug("TcpReader: load - attempting to load as JSON")
            loadobj = json.loads(file_content)

            if isinstance(loadobj, type({})) and "type" in loadobj and loadobj["type"] == "TCP_JSON":
                logging.debug("TcpReader: load - JSON load successful, attempting to load in object")
                # Init new project using loaded data from dict
                obj = project.Project(params[0], load=loadobj["data"], save_location=self.filename, saved=True)
            else:
                # This isn't a well-formed json tcp file, abort
                logging.error("TcpReader: load - JSON file is not well-formed, type incorrect, aborting load")
                return False
        except ValueError:
            logging.debug("TcpReader: load - loading as JSON failed, attempting to load as pickle (legacy format)")
            try:
                legacyobj = self.unpickle_object(file_content)
                # Build a new-style project from the old-style one
                newdict = self.convert_tcproject(legacyobj)
                obj = project.Project(params[0], load=newdict, save_location=self.filename, saved=False)
            except Exception:
                # Any error indicates failure to load, abort
                logging.error("TcpReader: load - loading as pickle also fails, this isn't a valid .tcp file!")
                logging.error(traceback.format_exc())
                return False

        return obj

    def convert_tcproject(self, tcproj):
        """Convert an old-style tcproject object into a new style project one"""
        logging.info("TcpReader: convert_tcproject")
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
                "seasons": {
                    "snow": tcproj.winter(),
                },
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
        logging.debug("TcpReader: convert_tcproject - projdict to feed into new project is: %s" % repr(projdict))
        return projdict

    def unpickle_object(self, pickle_str, params=None):
        """Unpickle an object from the pickled string pickle_str, optionally call post_serialise with params"""
        logging.info("TcpReader: unpickle_object - WARNING: pickle-style .tcp projects are considered a legacy format!")
        obj = pickle.loads(pickle_str)

        if params is not None:
            logging.info("TcpReader: unpickle_object - running post_serialise")
            obj.post_serialise(params)

        logging.info("TcpReader: unpickle_object - unpickled object: %s" % repr(obj))
        return obj

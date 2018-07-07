# coding: UTF-8
#
# TileCutter User Interface Module
#            File Picker
#
# This class provides additional methods for filename input controls, including highlighting

import logging, os
import wx
import config
config = config.Config()

class filePicker(object):
    """Methods for text boxes displaying paths"""
    def __init__(self, parent):
        logging.info("tcui.filePicker: __init__")
        self.parent = parent

    def filePickerDialog(self, path1, path2=None, dialogText="", dialogFilesAllowed="", dialogFlags=None):
        """File picker dialog with additional methods"""
        logging.info("tcui.filePicker: filePickerDialog")

        if path2 == None:
            path2 = ""

        # If path exists, and is a file, or the path up to the last bit exists and is a directory
        if (os.path.isfile(os.path.join(os.path.split(path2)[0], path1))
         or os.path.isfile(os.path.join(path2, path1))
         or os.path.isdir(os.path.join(path2, os.path.split(path1)[0]))
         or os.path.isdir(os.path.join(os.path.split(path2)[0], os.path.split(path1)[0]))
        ):
            a = os.path.join(os.path.split(path2)[0], os.path.split(path1)[0])
            b = os.path.split(path1)[1]
        # If path exists, and is a directory
        elif (os.path.isdir(os.path.join(os.path.split(path2)[0], path1))
           or os.path.isdir(os.path.join(path2, path1))
        ):
            a = os.path.join(os.path.split(path2)[0], path1)
            b = ""
        # If path does not exist
        else:
            # Assume that the last component of the png path is the filename, and find the largest component of the dat
            # path which exists
            a = self.existingPath(path2)
            b = os.path.split(path1)[1]

        # If path directory component empty, use passed-in "last" path as starting location
        # rather than using default starting location
        if path1 == "" and config.last_save_path != "" and os.path.exists(config.last_save_path):
            a = config.last_save_path

        logging.debug("Path a is: %s and path b is: %s" % (a, b))

        # Check path components exist

        # Show the dialog
        pickerDialog = wx.FileDialog(self.parent, dialogText, a, b, dialogFilesAllowed, dialogFlags)

        if pickerDialog.ShowModal() == wx.ID_OK:
            logging.debug("tcui.filePicker: filePickerDialog - File picker dialog, ID_OK, Directory is: %s, Filename is: %s" % (pickerDialog.GetDirectory(), pickerDialog.GetFilename()))

            # This needs to calculate a relative path between the location of the output png and the location of the output dat
            drivesplit = os.path.splitdrive(pickerDialog.GetDirectory())

            if drivesplit[0] != "" and drivesplit[1] == "":
                # There is a drive specified in the string, and nothing else in the path
                # If this directory was joined to the filename we'd get "D:filename.tcp" rather than "D:\filename.tcp"
                # So add an additional os.path.sep between the two
                value = os.path.join(pickerDialog.GetDirectory() + os.path.sep, pickerDialog.GetFilename())
                # Update last save path location (for next file browse action)
                config.last_save_path = pickerDialog.GetDirectory() + os.path.sep
            else:
                value = os.path.join(pickerDialog.GetDirectory(), pickerDialog.GetFilename())
                # Update last save path location (for next file browse action)
                config.last_save_path = pickerDialog.GetDirectory()
            relative = self.comparePaths(value, path2)
            pickerDialog.Destroy()
            return relative
        else:
            # Else cancel was pressed, do nothing
            return path1

    # Needs to be recoded to use generator/list comprehension stuff
    # Also needs to add caching of directory existance check and more intelligent updating based on the editing position of the
    # text entry, maybe even make this a persistent object modified along with the text entry

    # Three paths - Current Working Directory (typically where the script is run from)
    #             - .dat file directory, which is either given as an absolute path or is taken to be relative to CWD
    #             - .png file directory, which is either given as an absolute path (and must be turned into a relative path
    #               to the .dat file) or as a relative path to the .dat file (which needs to be turned into an absolute path
    #               for actual file output)
    #
    # So need:      Abspath, CWD        (to turn relative .dat path into absolute one)
    #               Abspath, .dat       (output location of the file)   From: either absolute path or one relative to CWD
    #               Relpath, .dat->.png (to write into the .dat file)   From: either relative path to .dat, or absolute one
    #               Abspath, .png       (output location of the file)   From: either relative path to .dat, or absolute one

    # .png display as relative path

    def highlightText(self, box, p1, p2=None):
        """Update the highlighting in a text entry box"""
        logging.info("tcui.filePicker: highlightText")
        logging.debug("highlightText, p1: %s, p2: %s" % (p1, p2))

        # Path value, optionally relative to a second path
        a = self.splitPath(p1, p2)
        logging.debug(str(a))

        # Set entire length of the box to default colour
        box.SetStyle(0, len(p1), wx.TextAttr(None, "white"))

        # Then recolour both boxes to reflect path existence
        for k in range(len(a)):
            # If this path section exists, colour it white
            if a[k][3]:
                box.SetStyle(a[k][1], a[k][1] + a[k][2], wx.TextAttr(None, "white"))
            # If path section doesn't exist, colour it yellow
            else:
                box.SetStyle(a[k][1], a[k][1] + a[k][2], wx.TextAttr(None, "#FFFF00"))

    # All of this file manipulation stuff could potentially be built into an extended text control

    # Path manipulation functions
    # splitPath     breaks a string up into path components
    # joinPaths     joins two paths together, taking end components (filenames etc.) into account
    # existingPath  returns the largest section of a path which exists on the filesystem
    # comparePaths  produces a relative path from two absolute ones

    def splitPath(self, p1, p2=None):
        """Split a path into an array, index[0] being the first path section, index[len-1] being the last
        Optionally takes a second path which is joined with the first for existence checks, to allow for
        checking existence of relative paths"""
        logging.info("tcui.filePicker: splitPath")

        if os.path.split(p1)[1] == "":
            # Check to make sure there isn't a trailing slash
            if os.path.split(os.path.split(p1)[0])[1] != "":
                p1 = os.path.split(p1)[0]

        a = []

        if p2 == None:
            p2 = ""

        while os.path.split(p1)[1] != "":
            n = os.path.split(p1)
            # Add at front, text,   offset,             length,     exists or not,      File or Directory?
            logging.debug("path1: %s, path2: %s" % (p1, p2))
            logging.debug("exists? %s, %s" % (self.joinPaths(p2, p1), os.path.exists(self.joinPaths(p2, p1))))
            a.insert(0, [n[1], len(p1) - len(n[1]), len(n[1]), os.path.exists(self.joinPaths(p2, p1))])
            p1 = n[0]

        return a

    def joinPaths(self, p1, p2):
        """Join p2 to p1, accounting for end cases (is directory, is file etc.)"""
        logging.info("tcui.filePicker: joinPaths")

        if p1 != None:
            # Need to check the end component
            if os.path.isfile(p1):
                # If it's a file that exists, split the directory off
                p1 = os.path.split(p1)[0]
            elif not os.path.isdir(p1):
                # If the path isn't a file which exists, and isn't a directory, split the end bit off
                # (Assume it's a file which hasn't been created yet)
                p1 = os.path.split(p1)[0]
        else:
            p1 = ""

        return os.path.join(p1, p2)

    def existingPath(self, p):
        """Take a path and return the largest section of this path that exists
        on the filesystem"""
        logging.info("tcui.filePicker: existingPath")

        if os.path.split(p)[1] == "":
            # Check to make sure there isn't a trailing slash
            if os.path.split(os.path.split(p)[0])[1] != "":
                p = os.path.split(p)[0]

        while not os.path.exists(p):
            q = p
            p = os.path.split(p)[0]
            # Avoid infinite loop
            if p == q:
                return ""

        return p

    def comparePaths(self, p1, p2):
        """Compare two absolute paths, returning either a relative path from p1 to p2, or p1 if no relative path exists"""
        logging.info("tcui.filePicker: comparePaths")

        # Check that p2 is not an empty string, or None, and that drive letters match
        if p2 == None or p2 == "" or os.path.splitdrive(p1)[0] != os.path.splitdrive(p2)[0]:
            return p1

        p1s = self.splitPath(os.path.normpath(p1))
        p2s = self.splitPath(os.path.normpath(p2))
        k = 0

        while p1s[k][0] == p2s[k][0]:
            k += 1

        # Number of /../'s is length of p2s minus k (number of sections which match, but remember this will be one more
        # than the number which match, which is what we want as the length is one more than we need anyway
        p3 = ""

        # If p2's last component is a file, need to subtract one more to give correct path
        e = 1

        for a in range(len(p2s)-k-e):
            p3 = os.path.join(p3, "..")

        # Then just add on all of the remaining parts of p1s past the sections which match
        for a in range(k,len(p1s)):
            p3 = os.path.join(p3, p1s[a][0])

        return p3

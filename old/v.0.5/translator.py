#
# TileCutter translation module
#
# Part of the TileCutter project
#

import wx
import sys, os, ConfigParser, StringIO, re, codecs
import imres
# Custom platform codecs
import u_newlines, w_newlines

# Translation setup
PATH_TO_TRANSLATIONS = "languages"
TRANSLATION_FILE_EXTENSION = ".tab"
DEFAULT_LANGFILE_ENCODING = "utf-8"

class Translator:
    """Contains all available translations as well as the active translation"""
    def __init__(self):
        """Load translation files"""
        # Obtain directory listing of available languages
        list = os.listdir(PATH_TO_TRANSLATIONS)
        language_file_list = []
        for i in list:
            split = os.path.splitext(i)
            if split[1] == TRANSLATION_FILE_EXTENSION:
                language_file_list.append(PATH_TO_TRANSLATIONS + os.path.sep + i)
        # Next produce a translation object for each file in language_file_list
        self.language_list = []
        self.language_names_list = []
        self.language_longnames_list = []
        for i in range(len(language_file_list)):
            self.language_list.append(translation(language_file_list[i]))
            self.language_names_list.append(self.language_list[i].name())
            self.language_longnames_list.append(self.language_list[i].longname())
        # Make dicts
        self.longnametoname = self.arraysToDict(self.language_longnames_list, self.language_names_list)
        self.nametotranslation = self.arraysToDict(self.language_names_list, self.language_list)

        # Should obtain this from the program settings object, similarly, when setting translation need to update program setting
        self.setActiveTranslation("base_translation")
##        debug.out(str(self.nametotranslation))
    def gt(self, text):
        """Return translated version of a string"""
        text = unicode(text)
        try:
            return self.active.translation[text]
        except KeyError:
            # If there is no translation for this item use the default program string
            return text

    def arraysToDict(self, keys, values):
        """Convert two arrays into a dict (assuming keys[x] relates to values[x])"""
        newdict = {}
        newdict.fromkeys(keys)
        for i in range(len(values)):
            newdict[keys[i]] = values[i]
        return newdict
    def longnameToName(self, longname):
        """Converts a long translation name to the short version"""
        return self.longnametoname[longname]
    def setActiveTranslation(self, name):
        """Set which translation should be used"""
        self.active = self.nametotranslation[name]

class translation:
    """An individual translation file object"""
    def __init__(self, filename):
        """Load translation, translation details and optionally a translation image"""
        # Open file & read in contents
        f = open(filename, "r")
        block = f.read()
        f.close()
        # Lanuage files should be saved as UTF-8
        block = block.decode("utf-8")
        # Convert newlines to unix style
        block = block.decode("u_newlines")
        # Init StringIO and ConfigParser
        sio = StringIO.StringIO()
        cfgparser = ConfigParser.SafeConfigParser()
        # Config, everything within [setup][/setup]
        configitems = re.findall("(?=\[setup\]).+(?=\n\[/setup\])", block, re.DOTALL)[0]
        configitems_lines = re.split("\n", configitems)
        for i in configitems_lines:
            sio.write(i + u"\n")
        sio.flush()
        sio.seek(0)
        cfgparser.readfp(sio)
        sio.close()
        # Can now query config items using cfgparser
        # name and name_translated are the only mandatory values
        if cfgparser.has_section("setup"):
            if cfgparser.has_option("setup", "name"):
                self.name(cfgparser.get("setup", "name"))
            else:
                # Translation file invalid
                pass
            if cfgparser.has_option("setup", "name_translated"):
                self.longname(cfgparser.get("setup", "name_translated"))
            else:
                # Translation file invalid
                pass
            if cfgparser.has_option("setup", "language_code"):
                self.language_code(cfgparser.get("setup", "language_code"))
            else:
                self.language_code("N/A")
            if cfgparser.has_option("setup", "created_by"):
                self.created_by(cfgparser.get("setup", "created_by"))
            else:
                self.created_by("Unknown")
            if cfgparser.has_option("setup", "created_date"):
                self.created_date(cfgparser.get("setup", "created_date"))
            else:
                self.created_date("Unknown")
            if cfgparser.has_option("setup", "icon"):
                self.icon(cfgparser.get("setup", "icon"))
            else:
                self.icon("default")
        # Remove config section from the block
        block = re.split("\[/setup\]\n", block, re.DOTALL)[1]
        # Then split it up into lines
        block_lines = re.split("\n", block)
        # Delete all items of block_lines which begin with "#"
        block_lines2 = []
        # Two pass system, first strip out comments
        for i in range(len(block_lines)):
            if len(block_lines[i]) != 0:
                if block_lines[i][0] != "#":
                    block_lines2.append(block_lines[i])
            else:
                block_lines2.append(block_lines[i])
        # Second check for and strip duplicate empty lines, single empty lines should be replaced by the translation key line
        block_lines3 = []
        for i in range(len(block_lines2)):
            if len(block_lines2[i]) == 0:                       # If empty line
                if i != 0 and len(block_lines3) != 0:           # If not first line in the file, and one non-empty line has been found
                    if len(block_lines2[i-1]) != 0:             # If line before this not empty
                        block_lines3.append(block_lines3[-1])   # Duplicate previous line
            else:
                block_lines3.append(block_lines2[i])            # If not an empty line
        # Check that block_lines2 is an even number of items, if not remove the last one
        # (The array of items must be an even number not including comments)
        # Now need to check through for escaped characters (\n mostly) and convert them to non-escaped versions
        for i in range(len(block_lines3)):
            block_lines3[i] = block_lines3[i].replace("\\n","\n")
        # Then go over the rest, two lines at a time, first line key, second line translation
        translation = {}
        keys = []
        values = []
        for i in range(0, len(block_lines3), 2):
            # Populate keys and values lists
            keys.append(block_lines3[i])
            try:
                values.append(block_lines3[i+1])
            except IndexError:
                print block_lines2[i]
        # Make dict from keys
        translation.fromkeys(keys)
        # Populate dict with values
        for i in range(len(values)):
            translation[keys[i]] = values[i]

        self.translation = translation

    def name(self, value=None):
        """Return or set the name of this translation"""
        if value != None:
            self.value_name = value
        else:
            return self.value_name
    def longname(self, value=None):
        """Return or set the translated name"""
        if value != None:
            self.value_longname = value
        else:
            return self.value_longname
    def language_code(self, value=None):
        """Return or set the country/language code"""
        if value != None:
            self.value_language_code = value
        else:
            return self.language_code
    def created_by(self, value=None):
        """Return or set the created by string"""
        if value != None:
            self.value_created_by = value
        else:
            return self.value_created_by
    def created_date(self, value=None):
        """Return or set the created on value"""
        if value != None:
            self.value_created_date = value
        else:
            return self.value_created_date
    def icon(self, value=None):
        """Return the translation's icon image, takes a path as input"""
        if value != None:
            if os.path.exists(PATH_TO_TRANSLATIONS + os.path.sep + value):
                self.value_icon = wx.Bitmap(PATH_TO_TRANSLATIONS + os.path.sep + value)
            else:
                self.value_icon = imres.catalog['tc_icon2_48_plain'].getBitmap()
        else:
            return self.value_icon

# coding: UTF-8
#
# TileCutter translation module
#

# Copyright © 2008-2010 Timothy Baldock. All Rights Reserved.


import wx
import sys, os, re, codecs
import imres
# Custom platform codecs
import u_newlines
import w_newlines
import json

import logger
debug = logger.Log()

##def gt(text):
##    lator = Translator()
##    return lator.gt(text)

# Translator is an object which contains a list of all the available translations
# as well as storing the currently active translation

# translation is an object containing all the information relating to
# an individual translation set

class Translator(object):
    """Contains all available translations as well as the active translation"""
    language_list = None
    # Translation setup
    PATH_TO_TRANSLATIONS = "languages"
    TRANSLATION_FILE_EXTENSION = ".tab"
    DEFAULT_LANGFILE_ENCODING = "utf-8"
    def __init__(self):
        """Load translation files"""
        if Translator.language_list is None:
            # Obtain directory listing of available languages
            list = os.listdir(Translator.PATH_TO_TRANSLATIONS)
            language_file_list = []
            for i in list:
                split = os.path.splitext(i)
                if split[1] == Translator.TRANSLATION_FILE_EXTENSION:
                    language_file_list.append(Translator.PATH_TO_TRANSLATIONS + os.path.sep + i)
            # Next produce a translation object for each file in language_file_list
            Translator.language_list = []
            Translator.language_names_list = []
            Translator.language_longnames_list = []
            for i in range(len(language_file_list)):
                Translator.language_list.append(translation(language_file_list[i]))
                Translator.language_names_list.append(Translator.language_list[i].name())
                Translator.language_longnames_list.append(Translator.language_list[i].longname())
            # Make dicts
            Translator.longnametoname = self.arraysToDict(Translator.language_longnames_list, Translator.language_names_list)
            Translator.nametotranslation = self.arraysToDict(Translator.language_names_list, Translator.language_list)

            # Should obtain this from the program settings object, similarly, when setting translation need to update program setting
            self.setActiveTranslation("english_translation")

    def __call__(self, vars):
        """Used so we can do Translator() and call gt()"""
        return self.gt(vars)

    def loop(self, text):
        """Just return the provided value, used for _gt() functionality"""
        return text

    def gt(self, text):
        """Return translated version of a string"""
        text = unicode(text)
        try:
            return Translator.active.translation[text]
        except KeyError:
            # If there is no translation for this item use the default program string
            return text

    def translateIntArray(self, intlist):
        """Takes an array of int values and translates them"""
        stringlist = []
        for i in intlist:
            stringlist.append(self.gt(str(i)))
        return stringlist

    def arraysToDict(self, keys, values):
        """Convert two arrays into a dict (assuming keys[x] relates to values[x])"""
        newdict = {}
        newdict.fromkeys(keys)
        for i in range(len(values)):
            newdict[keys[i]] = values[i]
        return newdict
    def longnameToName(self, longname):
        """Converts a long translation name to the short version"""
        return Translator.longnametoname[longname]
    def setActiveTranslation(self, name):
        """Set which translation should be used"""
        Translator.active = Translator.nametotranslation[name]

class TranslationLoadError(Exception):
    """Error class for exceptions raised by translation parser"""
    pass

class translation:
    """An individual translation file object"""
    def __init__(self, filename):
        """Load translation, translation details and optionally a translation image"""
        debug("Begin loading translation from file: %s" % filename)
        # Open file & read in contents
        try:
            f = open(filename, "r")
            block = f.read()
            f.close()
        except IOError:
            debug("Problem loading information from file, aborting load of translation file")
            raise TranslationLoadError()
        # Lanuage files should be saved as UTF-8
        block = block.decode("utf-8")
        # Convert newlines to unix style
        block = block.decode("u_newlines")
        # Scan document for block between {}, this is our config section
        dicts = re.findall("(?={).+?(?<=})", block, re.DOTALL)
        if len(dicts) != 1:
            debug("Error loading translation file: %s. Too many dicts found, ensure {} characters are not used in translation file" % filename)
            raise TranslationLoadError()
        configstring = dicts[0]
        
        debug("Translation file config string is: %s" % configstring)

        config = json.loads(configstring)
        conf_items = ["name", "name_translated", "language_code", "created_by", "created_date"]
        func_items = [self.name, self.longname, self.language_code, self.created_by, self.created_date]
        for ci, func in zip(conf_items, func_items):
            if config.has_key(ci):
                func(config[ci])
            else:
                # Translation file invalid, error out of read process
                debug("Error loading translation from %s, %s field not found, aborting load of translation" % (filename, ci))
                raise TranslationLoadError()

        # Split block up into lines
        block_lines = re.split("\n", block)
        block_lines2 = []
        # Delete all items of block_lines which begin with "#"
        # Two pass system, first strip out comments
        for line in block_lines:
            if len(line) != 0 and line[0] != "#":
                block_lines2.append(line)
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

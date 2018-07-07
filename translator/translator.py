# coding: UTF-8
#
# TileCutter translation module

import logging, codecs, json, os, re
import config
config = config.Config()
config.save()

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
    DEFAULT_LANGFILE_ENCODING = "UTF-8"

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

            # Activate translation based on user preferences
            # If preference does not exist, use English instead
            if config.default_language in Translator.language_names_list:
                active = config.default_language
                logging.info("Language setting found in config file - Setting active translation to %s" % active)
            else:
                active = "English"
                logging.info("Using default language - Setting active translation to %s" % active)

            self.setActiveTranslation(active)

    def __call__(self, vars):
        """Used so we can do Translator() and call gt()"""
        return self.gt(vars)

    def loop(self, text):
        """Just return the provided value, used for _gt() functionality"""
        return text

    def gt(self, text):
        """Return translated version of a string"""
        text = str(text)
        try:
            translation = Translator.active.translation[text]
            if len(translation) == 0:
                return text
            else:
                return translation
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
        # Save this preference for the user
        config.default_language = name

class TranslationLoadError(Exception):
    """Error class for exceptions raised by translation parser"""
    pass

class translation:
    """An individual translation file object"""

    def __init__(self, filename):
        """Load translation, translation details and optionally a translation image"""
        logging.info("Begin loading translation from file: %s" % filename)

        # Open file & read in contents
        try:
            # Language files should be saved as UTF-8 - this conversation done now by directly reading as UTF-8
            f = codecs.open(filename, "r", "UTF-8")
            block = f.read()
            f.close()
        except IOError:
            logging.error("Problem loading information from file, aborting load of translation file")
            raise TranslationLoadError()

        # Scan document for block between {}, this is our config section
        dicts = re.findall("(?={).+?(?<=})", block, re.DOTALL)

        if len(dicts) > 1:
            logging.warn("Found more than one dict-like structure (e.g. pair of \"{}\") in file: \"%s\" - assuming config is the first one" % filename)

        configstring = dicts[0]

        ## logging.debug("Translation file config string is: %s" % configstring)

        config = json.loads(configstring)
        conf_items = ["name", "name_translated", "language_code", "created_by", "created_date"]
        func_items = [self.name, self.longname, self.language_code, self.created_by, self.created_date]

        for ci, func in zip(conf_items, func_items):
            if ci in config:
                func(config[ci])
            else:
                # Translation file invalid, error out of read process
                logging.error("Error loading translation from %s, %s field not found, aborting load of translation" % (filename, ci))
                raise TranslationLoadError()

        # Split block up into lines
        block_lines = re.split("\n", block)
        block_lines2 = []

        # Delete all items of block_lines which begin with "#"
        # Two pass system, first strip out comments
        for line in block_lines:
            if len(line) != 0:
                if line[0] != "#":
                    block_lines2.append(line)
            else:
                block_lines2.append(line)

        # Translation is made up of key\nvalue\n pairs, the keys must be on odd-numbered lines, values on even (after comments are stripped)
        # Blank lines can only occur on even numbered lines since a blank cannot be a key. Thus we need to normalise the file for duplicate newlines
        # while keeping this in mind.

        # Starting with first line
        # Looking for key - Is line blank? If so discard it and start over
        # Looking for key - If first line isn't blank assume it is key, remove from stack
        # Looking for value - If next line is blank, assume it's a blank value, remove from stack
        # Start over looking for a key

        block_lines3 = []
        looking_for_key = True

        for i in block_lines2:
            if looking_for_key:
                if len(i) != 0:
                    block_lines3.append(i)
                    looking_for_key = False
            else:
                block_lines3.append(i)
                looking_for_key = True

        # Check that block_lines3 is an even number of items, if not remove the last one
        # (The array of items must be an even number not including comments)
        # Now need to check through for escaped characters (\n mostly) and convert them to non-escaped versions
        for i in range(len(block_lines3)):
            block_lines3[i] = block_lines3[i].replace("\\n", "\n")

        # Then go over the rest, two lines at a time, first line key, second line translation
        translation = {}
        keys = []
        values = []

        for i in range(0, len(block_lines3), 2):
            # Populate keys and values lists
            keys.append(block_lines3[i])
            try:
                values.append(block_lines3[i + 1])
            except IndexError:
                print(block_lines2[i])

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

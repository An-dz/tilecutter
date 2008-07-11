# TileCutter translation string finder
# Version 0.2 for TileCutter v.0.5

import re, time, os, codecs
import u_newlines, w_newlines

VERSION_NUMBER = "0.2"
COMPAT_VERSION_NUMBER = "0.5"
# Should duplicate translator entries be outputted to the translation file?
WRITE_DUPLICATES=0
FILE_ENCODING = "utf-8"
ENCODE_WIN = True

logging = False

# This script finds translation strings in TileCutter and outputs them
# in a format SimuTranslator can understand


# All files to be scanned should be entered in this list
components = ["TileCutter5.py"]

# Name of output file
outputfile = "languages" + os.path.sep + "tc_xx.tab"
if logging:
    logfile = "tct.log"

# This script searches for instances of "gt(", then copies everything from
# that up to the following non-escaped ")" into the output file. If a duplicate
# translation string is located the script will flag it in the output file and
# produce a message on the standard error output

# Limitations:
# Multi-line translation strings - Newlines inside translation strings will be
#   stripped if not escaped
# 

f = codecs.open(outputfile, "w", encoding=FILE_ENCODING)
if ENCODE_WIN:
    outfile = codecs.EncodedFile(f, "w_newlines")
else:
    outfile = f
if logging:
    error_file = open(logfile, "w")

name = u"base_translation"
name_translated = u"Base Translation"
language_code = u"XX"
created_by = u"Timothy Baldock"
created_date = time.strftime(u"%d-%m-%Y")
flag = u"tc_xx.png"

outfile.write(u"""[setup]
name = %s
name_translated = %s
language_code = %s
created_by = %s
created_date = %s
icon = %s
[/setup]
#
#
#	** Base translation file for TileCutter **
#	
#
#	File Encoding: UTF-8
#
#	Produced using TileCutterTranslator version %s for TileCutter version %s
#	On (%s)
#
#	* Translation keys are provided, translation string should be on the line below
#	* Entries with tt before them are tooltips (usually)
#	* Where "&" appears in a string, the next character will be a control character,
#	  "%s" indicates a number goes here, "%s" indicates a program-generated string goes here
#	  these are required!! The key should give an indication of how they work...
#
#	"#" indicates line is a comment, you can escape it with "\\" in case of lines starting with "#"
#
#
""" % (name, name_translated, language_code, created_by, created_date, flag,
       VERSION_NUMBER, COMPAT_VERSION_NUMBER, time.strftime("%d-%B-%Y"), "%i", "%s"))


if logging:
    error_file.write("-------------------------------------------\n")
    error_file.write("TileCutterTranslator version %s - log file\n"%VERSION_NUMBER)
    error_file.write("-------------------------------------------\n\n")

t_array = []

# For each of the components listed
block = ""
for x in components:
    if logging:
        error_file.write("Extracting file: %s\n" % x)
    working = open(x, "r")
    block += working.read()
    working.close()

# Now use regex to find all translation strings in the file
rawstrings = re.findall("(?<=gt\(\").+?(?=\"\))", block)

# Strip duplicates
strings = []
for i in rawstrings:
    if i not in strings:
        strings.append(i)
        # Output these strings to a file
        outfile.write(unicode(i) + u"\n\n")
##        outfile.write(i + "\n" + i + "\n")

outfile.write(u"#End of File - Total of %i strings" % len(strings))
if logging:
    error_file.write("...Process completed, found %i translation strings" % len(strings))

outfile.close()
if logging:
    error_file.close()













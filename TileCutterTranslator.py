# coding: UTF-8
#
# TileCutter translation string finder
# Version 0.3 for TileCutter v.0.5
#

# Copyright © 2008-2009 Timothy Baldock. All Rights Reserved.

import re, time, os, codecs
import translator.w_newlines as w_newlines
import translator.u_newlines as u_newlines

VERSION_NUMBER = "0.3"
COMPAT_VERSION_NUMBER = "0.5"
# Should duplicate translator entries be outputted to the translation file?
FILE_ENCODING = "utf-8"
ENCODE_WIN = False

logging = True

# This script finds translation strings in TileCutter and outputs them
# in a format SimuTranslator can understand

print os.getcwd()
# All files and directories to be scanned should be entered in this list (directory scanning is not recursive)
components = ["TileCutter5.pyw", "tcui", ]
# For directories, specify a list of valid extensions to scan
component_valid_extensions = [".py"]

# Pre-process components list to expand directories
new_components = []
for c in components:
    if os.path.isdir(c):
        dir = os.listdir(c)
        for d in dir:
            if os.path.splitext(d)[1] in component_valid_extensions:
                new_components.append(os.path.join(c, d))
    else:
        new_components.append(c)

components = new_components

# Name of output file
outputfile = "languages" + os.path.sep + "tc_test.tab"
outputfile = "tc_test.tab"
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
created_by = u"Auto-Generated"
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













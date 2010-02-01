# coding: UTF-8
#
# TileCutter translation string finder
# Version 0.4 for TileCutter v.0.5
#

# Copyright © 2008-2010 Timothy Baldock. All Rights Reserved.

import re, time, os, codecs
import translator.w_newlines as w_newlines
import translator.u_newlines as u_newlines
import json

VERSION_NUMBER = "0.4"
COMPAT_VERSION_NUMBER = "0.5"
# Should duplicate translator entries be outputted to the translation file?
FILE_ENCODING = "utf-8"
ENCODE_WIN = False

logging = True

# This script finds translation strings in TileCutter and outputs them
# in a format SimuTranslator can understand

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
dbfile = os.path.join("languages", "tc_en.db")
outputfile = os.path.join("languages", "tc_en.tab")
stfile = os.path.join("languages", "tc_simutranslator.dat")

if logging:
    logfile = "tct.log"

tdict = {}

# Open existing db file (if this exists)
try:
    f = open(dbfile, "r")
    db = json.loads(f.read())
    f.close()
except IOError:
    db = {}

# This script searches for instances of "gt(", then copies everything from
# that up to the following non-escaped ")" into the output file. If a duplicate
# translation string is located the script will flag it in the output file and
# produce a message on the standard error output

# Limitations:
# Multi-line translation strings - Newlines inside translation strings will be
#   stripped if not escaped
# 

# Open file for english (default) translation output
f = codecs.open(outputfile, "w", encoding=FILE_ENCODING)
if ENCODE_WIN:
    outfile = codecs.EncodedFile(f, "w_newlines")
else:
    outfile = f

# Open log file
if logging:
    error_file = open(logfile, "a")

# Open file for simutranslator output
f = codecs.open(stfile, "w", encoding=FILE_ENCODING)
if ENCODE_WIN:
    stoutfile = codecs.EncodedFile(f, "w_newlines")
else:
    stoutfile = f

name = u"english_translation"
name_translated = u"English"
language_code = u"EN"
created_by = u"Timothy Baldock"
created_date = time.strftime(u"%d-%m-%Y")

outfile.write(u"""#{"name": "%s", "name_translated": "%s", "language_code": "%s", "created_by": "%s", "created_date": "%s"}
#
#	** English translation file for TileCutter **
#
#	File Encoding: UTF-8
#
#	Produced using TileCutterTranslator version %s for TileCutter version %s
#	On (%s)
#
#	* Translation keys are provided, translation string should be on the line below
#   * The information at the head of the file must exist for the translation file to be valid
#	* Entries with tt before them are tooltips
#	* Where "&" appears in a string, the next character will be a control character,
#	  "%s" indicates a number goes here, "%s" indicates a program-generated string goes here
#	  these are required!! The key should give an indication of how they work...
#
#	"#" indicates line is a comment, you can escape it with "\\" in case of lines starting with "#"
#
#
""" % (name, name_translated, language_code, created_by, created_date, 
       VERSION_NUMBER, COMPAT_VERSION_NUMBER, time.strftime("%d-%B-%Y"), "%i", "%s"))


if logging:
    error_file.write("--------------------------------------------------------------------------\n")
    error_file.write("TileCutterTranslator version %s - log file\n"%VERSION_NUMBER)

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

strings = []
dupestrings = []
# For each entry in rawstrings, check if it's in the DB
for s in rawstrings:
    if s not in db.keys():
        # If there's no key for this, add one
        if logging:
            error_file.write("New key found: %s\n" % s)
        db[s] = ""
    # Check if this is a duplicate, and add to the list if so
    if s in strings and s not in dupestrings:
        if logging:
            error_file.write("Duplicate found: %s\n" % s)
        dupestrings.append(s)
    strings.append(s)

# Write out the DB
f = open(dbfile, "w")
f.write(json.dumps(db, sort_keys=True, indent=4))
f.close()

# Next write out all entries in the DB to the translation file
for k, v in db.items():
    outfile.write(u"%s\n%s\n" % (unicode(k), unicode(v)))

# Also write them out to the simutranslator file ready for import
# Include the obj= and name= bits at the start of each one, with a ---- seperator between them
for k, v in db.items():
    stoutfile.write(u"obj=program_text\nname=%s\n----------\n" % unicode(k))

outfile.write(u"#End of File - Total of %i string pairs\n" % len(db))
if logging:
    error_file.write("...Process completed, output %i translation string pairs\n" % len(db))

outfile.close()
stoutfile.close()
if logging:
    error_file.close()













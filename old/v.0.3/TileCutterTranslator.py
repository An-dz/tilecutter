# TileCutter translation string finder
# Version 0.1

VERSION_NUMBER = "0.1"
# Should duplicate translator entries be outputted to the translation file?
WRITE_DUPLICATES=0

# This script finds translation strings in TileCutter and outputs them
# in a format SimuTranslator can understand

# All files to be scanned should be entered in this list
components = ["TileCutter-transtest.py"]

# Name of output file
output = "tc-test.tab"

# Component section delimiter
# Written in a comment after each component is read, %s is the name of the
# component file (must be included!)
comp_del = "----------%s----------"

# Duplicate flag
# How duplicate translation entries should be flagged up in the output
# Will be placed above entries which are duplicated
dupe_flag = "------DUPLICATE!-----"

# This script searches for instances of "gt(", then copies everything from
# that up to the following non-escaped ")" into the output file. If a duplicate
# translation string is located the script will flag it in the output file and
# produce a message on the standard error output

# Limitations:
# Multi-line translation strings - Newlines inside translation strings will be
#   stripped if not escaped
# 

outfile = open(output, "w")
error_file = open("tct.log", "w")

t_array = []

outfile.write("""Base Translation
#
#
#	** Base translation file for TileCutter **
#	
#
#	File Encoding: UTF-8
#
#	Version %s (18-July-2006) - Timothy Baldock
#
#	* Translation keys are provided, translation string should be on the line below
#	* Entries with tt before them are tooltips (usually)
#	* Where "&" appears in a string, the next character will be a control character,
#	  "%i" indicates a number goes here, "%s" indicates a program-generated string goes here
#	  these are required!! The key should give an indication of how they work...
#	* The first line of this file **must** be the translated name of the language for
#	  the file e.g. "English" for English, or "Deutsch" for German
#
#
#
""")


error_file.write("-------------------------------------------\n")
error_file.write("TileCutterTranslator version %s - log file\n"%VERSION_NUMBER)
error_file.write("-------------------------------------------\n\n")

# For each of the components listed
for x in range(len(components)):
    outfile.write("# " + comp_del%components[x] + "\n")
    error_file.write("Extracting strings from file: %s\n\n"%components[x])
    working = open(components[x], "r")
    block = working.read()
    working.close()
    k = 0
    while k != 1:
        tuple = block.partition("gt(\"")
        # First part of tuple will be everything up to this point, trash
        # Second part will be the translation function opening string
        # Third part is what we want
        tuple2 = tuple[2].partition("\")")
        # First part is our translation string
        # First, check if this translation string has already been used
        if tuple2[0] in t_array:
            # If this translation string has already been used, we need to
            # alert the user of this fact. Write to the log file indicating
            # the problem and put a note in the outputted file
            error_file.write("WARNING: Duplicate translation entry - \"%s\" found!\n"%tuple2[0])
            error_file.write("         Placing marker at position of duplication...\n\n")
            if WRITE_DUPLICATES == 1:
                outfile.write("# " + dupe_flag + "\n")
                outfile.write(tuple2[0] + "\n\n")
        else:
            t_array.append(tuple2[0])
            outfile.write(tuple2[0] + "\n\n")
        # Second part is the translation function closing string
        # Third part is the rest of the file, which we want to continue
        # working on
        block = tuple2[2]
        if block == "":
            k = 1

error_file.write("...Process completed, found %i translation strings"%len(t_array))

outfile.close()
error_file.close()













#!/usr/bin/env python

from distutils.core import setup
import sys, os, os.path

version = "0.5.2"

### this manifest enables the standard Windows XP-looking theme
##manifest = """
##<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
##<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
##manifestVersion="1.0">
##<assemblyIdentity
##    version="0.64.1.0"
##    processorArchitecture="x86"
##    name="Controls"
##    type="win32"
##/>
##<description>Picalo</description>
##<dependency>
##    <dependentAssembly>
##        <assemblyIdentity
##            type="win32"
##            name="Microsoft.Windows.Common-Controls"
##            version="6.0.0.0"
##            processorArchitecture="X86"
##            publicKeyToken="6595b64144ccf1df"
##            language="*"
##        />
##    </dependentAssembly>
##</dependency>
##</assembly>
##"""
##
# returns a list of all the files in a directory tree
def walk_dir(dirname):
    files = []
    ret = (dirname, files)
    for name in os.listdir(dirname):
        fullname = os.path.join(dirname, name)
        if os.path.isdir(fullname) and os.path.split(fullname)[1] != ".svn":
            ret.extend(walk_dir(fullname))
        else:
            if os.path.split(fullname)[1] != ".svn":
                files.append(fullname)
    return ret
  

# Generic options
options = {
    'name':             'TileCutter',
    'version':          version,
    'description':      'Simutrans Building Editor',
    'long_description': '',
    'author':           'Timothy Baldock',
    'author_email':     'tb@entropy.me.uk',
    'url':              'http://entropy.me.uk/tilecutter',
    "zipfile":          "python\\library.zip",
    "data_files":       [
                         ("", ["licence.txt", "tc.config", "test.png"]),
                         walk_dir("languages"),
                         ]
}

# windows specific
if len(sys.argv) >= 2 and sys.argv[1] == "py2exe":
    try:
        import py2exe
    except ImportError:
        print "Could not import py2exe. Aborting windows exe output"
        sys.exit(0)
    # windows-specific options
    options["windows"] = [
        {
        "script":"TileCutter5.pyw",
        "windows":"TileCutter5.pyw",
        "icon_resources": [(1, "TileCutter icon/tilecutter.ico"),(2, "TileCutter icon/tilecutter_document.ico")],
        },
    ]
#    options["data_files"] += [("", ["../dist/msvcp71.dll"]]
    options["options"] = {
        # Bundling of .dlls into the zip results in massively bigger package?!
        # Option 1 creates corrupt zip, option 2 adds dlls and makes them uncompressible
        "py2exe": {"dist_dir": "../dist/win_dist_%s" % version,
                   "bundle_files": 3,
                   "excludes": ["difflib", "doctest", "optparse", "calendar", "pdb", "inspect",
                                "Tkconstants", "Tkinter", "tcl"]
                   },
    }



# mac specific
##if len(sys.argv) >= 2 and sys.argv[1] == 'py2app':
##    try:
##        import py2app
##    except ImportError:
##        print 'Could not import py2app.   Mac bundle could not be built.'
##    sys.exit(0)
##    # mac-specific options
##    options['app'] = ['rur_start.py']
##    options['options'] = {
##    'py2app': {
##        'argv_emulation': True,
##        'iconfile': 'rur_images/icon_mac.icns',
##        'packages': [],
##        }
##    }


# run the setup
setup(**options)

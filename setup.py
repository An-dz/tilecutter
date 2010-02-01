#!/usr/bin/env python

from distutils.core import setup
import sys, os, os.path
import zipfile

version = "0.5.3-alpha"

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

# Pre-setup actions (py2exe, py2app & source preparation)



# Source distribution specific
if len(sys.argv) >= 2 and sys.argv[1] == "source":
    dist_dir = os.path.join("..", "dist", "src_dist_%s" % version)
    dist_zip = os.path.join("..", "dist", "TileCutter_src_%s.zip" % version) 

    # Needed files:
    # trunk/
    #       translator/*
    #       languages/*
    #       tcui/*
    #       config.py
    #       imres.py
    #       licence.txt
    #       logger.py
    #       tc.py
    #       tcproject.py
    #       test.png
    #       TileCutter5.pyw

    try:
        import shutil
    except ImportError:
        print "Could not import shutil module. Aborting source distribution creation"
        sys.exit(0)

    for recdir in ["translator", "languages", "tcui"]:
        print "Copying contents of: %s/" % recdir
        shutil.copytree(recdir, os.path.join(dist_dir, recdir), ignore=shutil.ignore_patterns(".svn", "tmp*", "*.pyc", "*.py~"))

    for distfile in ["config.py", "imres.py", "licence.txt", "logger.py", "tc.py", "tcproject.py", "test.png", "TileCutter5.pyw"]:
        print "Copying file: %s" % distfile
        shutil.copy(distfile, dist_dir)

    # After building this, run post-setup actions (e.g. creating distribution packages etc.)
    # Produce .zip file
    print "Adding distribution files to .zip..."
    zip = zipfile.ZipFile(dist_zip, "w", zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(dist_dir):
        for name in files:
            fn = os.path.join(root, name) 
            rel_fn = os.path.relpath(os.path.join(root, name), dist_dir) 
            print "  Adding \"%s\" to zip as \"%s\"" % (fn, rel_fn)
            zip.write(fn, rel_fn)
    zip.close()


# windows specific
if len(sys.argv) >= 2 and sys.argv[1] == "py2exe":
    dist_dir = os.path.join("..", "dist", "win_dist_%s" % version)
    dist_zip = os.path.join("..", "dist", "TileCutter_win_%s.zip" % version) 
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
        "icon_resources": [(1, "TileCutter icon/tilecutter.ico"),(42, "TileCutter icon/tilecutter_document.ico")],
        },
    ]
#    options["data_files"] += [("", ["../dist/msvcp71.dll"]]
    options["options"] = {
        # Bundling of .dlls into the zip results in massively bigger package?!
        # Option 1 creates corrupt zip, option 2 adds dlls and makes them uncompressible
        "py2exe": {"dist_dir": dist_dir,
                   "bundle_files": 3,
                   "excludes": ["difflib", "doctest", "optparse", "calendar", "pdb", "inspect",
                                "Tkconstants", "Tkinter", "tcl"]
                   },
    }

    # run the setup
    setup(**options)

    # After building this, run post-setup actions (e.g. creating distribution packages etc.)
    # Produce .zip file
    print "Adding distribution files to .zip..."
    zip = zipfile.ZipFile(dist_zip, "w", zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(dist_dir):
        for name in files:
            fn = os.path.join(root, name) 
            rel_fn = os.path.relpath(os.path.join(root, name), dist_dir) 
            print "  Adding \"%s\" to zip as \"%s\"" % (fn, rel_fn)
            zip.write(fn, rel_fn)
    zip.close()


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


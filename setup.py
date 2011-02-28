#!/usr/bin/env python
# coding: UTF-8
#
# TileCutter - Distribution build tools
#

# Copyright © 2008-2011 Timothy Baldock. All Rights Reserved.
#

from distutils.core import setup
#from setuptools import setup
import sys, os, os.path
import zipfile

version = "0.5.6.4"

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
    "name":             u"TileCutter",
    "version":          version,
    "description":      u"Simutrans Building Editor",
    "long_description": "",
    "author":           u"Timothy Baldock",
    "author_email":     u"tb@entropy.me.uk",
    "url":              u"http://entropy.me.uk/tilecutter",
    "zipfile":          "python\\library.zip",
    "data_files":       [
                         ("", ["licence.txt", "tc.config", "test.png"]),
                         walk_dir("languages"),
                         ]
}

# Pre-setup actions (py2exe, py2app & source preparation)



# Source distribution specific
if len(sys.argv) >= 2 and sys.argv[1] == "source":
    print "Running source distribution"
    try:
        import shutil
    except ImportError:
        print "Could not import shutil module. Aborting source distribution creation"
        sys.exit(1)

    dist_dir = os.path.join("..", "dist", "src_dist_%s" % version)
    dist_zip = os.path.join("..", "dist", "TileCutter_src_%s.zip" % version) 

    for recdir in ["translator", "languages", "tcui"]:
        print "Copying contents of: %s/" % recdir
        shutil.copytree(recdir, os.path.join(dist_dir, recdir), ignore=shutil.ignore_patterns(".svn", "tmp*", "*.pyc", "*.py~", "*.tab~"))

    for distfile in ["config.py", "imres.py", "licence.txt", "logger.py", "tcp.py", "tc.py", "tcproject.py", "test.png", "tilecutter.py", "tilecutter.pyw", "main.py"]:
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


# Windows specific
if len(sys.argv) >= 2 and sys.argv[1] == "py2exe":
    print "Running py2exe distribution"
    try:
        import py2exe
    except ImportError:
        print "Could not import py2exe. Aborting windows exe output"
        sys.exit(1)

    dist_dir = os.path.join("..", "dist", "win_dist_%s" % version)
    dist_zip = os.path.join("..", "dist", "TileCutter_win_%s.zip" % version)
    dist_msi = os.path.join("..", "dist", "TileCutter_win_%s.msi" % version)

    options["windows"] = [
        {
        "script":"tilecutter.py",
        "windows":"tilecutter.py",
        "icon_resources": [(1, "TileCutter icon/tilecutter.ico"),(42, "TileCutter icon/tcp.ico")],
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

    # Next, create MSI distribution


# OSX specific
if len(sys.argv) >= 2 and sys.argv[1] == "py2app":
    print "Running py2app distribution"
    try:
        import py2app
    except ImportError:
        print "Could not import py2app.   Mac bundle could not be built."
        sys.exit(1)

    dist_dir = os.path.join("..", "dist", "osx_dist_%s" % version)
    dist_dmg = os.path.join("..", "dist", "TileCutter_osx_%s.dmg" % version) 

    # See: http://developer.apple.com/library/mac/#documentation/FileManagement/Conceptual/understanding_utis/understand_utis_conc/understand_utis_conc.html
    # http://stackoverflow.com/questions/1771601/registering-an-icon-for-my-applications-document-type
    

    # Bindings to allow drag+drop of project files onto icon
    # Also registers filetype with OSX
    plist = {
                "CFBundleIdentifier": u"uk.me.entropy.tilecutter",
                "CFBundleGetInfoString": u"Simutrans Building Editor",
                "NSHumanReadableCopyright": u"Copyright © 2008-2011 Timothy Baldock. All Rights Reserved.",
                "CFBundleDocumentTypes": [
                    {
                        "CFBundleTypeName": u"TileCutter Project Document", 
                        "CFBundleTypeRole": u"Editor", 
                        "CFBundleTypeExtensions": [u"tcp",],
                        "LSItemContentTypes": [u"uk.me.entropy.tcp",],
                        "CFBundleTypeIconFile": u"tcp.icns",
                    },
                ],
                "UTExportedTypeDeclarations": [
                    {
                        "UTTypeIdentifier": u"uk.me.entropy.tcp", 
                        "UTTypeReferenceURL": u"http://entropy.me.uk/tilecutter/docs/tcpformat/",
                        "UTTypeDescription": u"TileCutter Project File",
                        "UTTypeIconFile": u"tcp.icns",
                        "UTTypeConformsTo": [u"public.data",],
                        "UTTypeTagSpecification": {
                            "com.apple.ostype": u"TCPF",
                            "public.filename-extension": [u"tcp",],
                            "public.mimetype": u"application/x-tilecutter-project",
                        },
                    },
                ],
            }

    # mac-specific options
    options["app"] = ["tilecutter.py"]
    options["options"] = {
        "py2app": {
            "dist_dir": dist_dir,
            "argv_emulation": True,
            "iconfile": "TileCutter icon/tilecutter.icns",
            "packages": [],
            "excludes": ["difflib", "doctest", "calendar", "pdb", "inspect",
                        "Tkconstants", "Tkinter", "tcl"],
            "site_packages": True,
            "resources": ["TileCutter icon/tcp.icns",],
            "plist": plist,
            }
    }
    options["setup_requires"] = ["py2app"]
    # run the setup
    setup(**options)

    # See: http://digital-sushi.org/entry/how-to-create-a-disk-image-installer-for-apple-mac-os-x/

    # Next run shell commands to interact with the .dmg package
    # Copy .dmg from location in source control to dist directory
    # Convert to sparseimage
    # Remove .dmg from dist
    # Mount sparseimage
    # Copy application bundle into sparseimage (to replace placeholder)
    # Unmount sparseimage
    # Convert to .dmg + compress


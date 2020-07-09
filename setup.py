#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Created by: python.exe -m py2exe tilecutter.py -W mysetup.py

from distutils.core import setup
import py2exe

# project import
import config
config = config.Config()


class Target(object):
    """
    Target is the baseclass for all executables that are created.
    It defines properties that are shared by all of them.
    """
    def __init__(self, **kw):
        self.__dict__.update(kw)

        # The 'version' attribute MUST be defined, otherwise no versioninfo will be built:
        self.version = config.version

        self.product_name = "TileCutter"
        self.file_description = "Simutrans Building Editor"
        self.product_version = config.version
        self.copyright = "Copyright © 2018-2020 André Zanghelini. Copyright © 2008-2015 Timothy Baldock."
        self.legal_copyright = "Copyright © 2018-2020 André Zanghelini. All Rights Reserved. Copyright © 2008-2015 Timothy Baldock. All Rights Reserved."
        # self.company_name = "Company Name"
        # self.legal_trademark = ""
        # self.comments = ""
        # self.internal_name = ""

        # self.private_build = "foo"
        # self.special_build = "bar"

    def copy(self):
        return Target(**self.__dict__)

    def __setitem__(self, name, value):
        self.__dict__[name] = value


RT_BITMAP = 2
RT_MANIFEST = 24

# A manifest which specifies the executionlevel
# and windows common-controls library version 6
manifest_template = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
    <assemblyIdentity
        version="5.0.0.0"
        processorArchitecture="*"
        name="%(prog)s"
        type="win32"
    />
    <description>%(prog)s</description>
    <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
        <security>
            <requestedPrivileges>
                <requestedExecutionLevel
                    level="%(level)s"
                    uiAccess="false">
                </requestedExecutionLevel>
            </requestedPrivileges>
        </security>
    </trustInfo>
    <dependency>
        <dependentAssembly>
            <assemblyIdentity
                type="win32"
                name="Microsoft.Windows.Common-Controls"
                version="6.0.0.0"
                processorArchitecture="*"
                publicKeyToken="6595b64144ccf1df"
                language="*"
            />
        </dependentAssembly>
    </dependency>
</assembly>
"""

tilecutter = Target(
    # path of the main script
    script = "tilecutter.py",

    # Allows to specify the basename of the executable, if different from 'tilecutter'
    dest_base = "TileCutter",

    # Icon resources:[(resource_id, path to .ico file), ...]
    icon_resources = [(1, r"graphics/tilecutter.ico"), (42, r"graphics/tcp.ico")],
    # bitmap_resources = [(1, "resources")],
    other_resources = [
        (RT_MANIFEST, 1, (manifest_template % {"prog": "tilecutter", "level": "asInvoker"}).encode("utf-8")),
        # for bitmap resources, the first 14 bytes must be skipped when reading the file:
        # (RT_BITMAP, 1, open("bitmap.bmp", "rb").read()[14:]),
    ],
)

# ``zipfile`` and ``bundle_files`` options explained:
# ===================================================
#
# zipfile is the Python runtime library for your exe/dll-files; it
# contains in a ziparchive the modules needed as compiled bytecode.
#
# If 'zipfile=None' is used, the runtime library is appended to the
# exe/dll-files (which will then grow quite large), otherwise the
# zipfile option should be set to a pathname relative to the exe/dll
# files, and a library-file shared by all executables will be created.
#
# The py2exe runtime *can* use extension module by directly importing
# the from a zip-archive - without the need to unpack them to the file
# system.  The bundle_files option specifies where the extension modules,
# the python dll itself, and other needed dlls are put.
#
# bundle_files == 3:
#     Extension modules, the Python dll and other needed dlls are
#     copied into the directory where the zipfile or the exe/dll files
#     are created, and loaded in the normal way.
#
# bundle_files == 2:
#     Extension modules are put into the library ziparchive and loaded
#     from it directly.
#     The Python dll and any other needed dlls are copied into the
#     directory where the zipfile or the exe/dll files are created,
#     and loaded in the normal way.
#
# bundle_files == 1:
#     Extension modules and the Python dll are put into the zipfile or
#     the exe/dll files, and everything is loaded without unpacking to
#     the file system.  This does not work for some dlls, so use with
#     caution.
#
# bundle_files == 0:
#     Extension modules, the Python dll, and other needed dlls are put
#     into the zipfile or the exe/dll files, and everything is loaded
#     without unpacking to the file system.  This does not work for
#     some dlls, so use with caution.

py2exe_options = {
    # see above
    "bundle_files": 1,
    # optimization level [string or int (0, 1, or 2)]
    "optimize": 2,
    # create a compressed zipfile
    # uncompressed may or may not have a faster startup
    "compressed": False,
    # directory where to build the final files
    "dist_dir": "dist",
    # comma-separated list of modules to exclude
    "excludes": ["wx.lib.colourutils", "calendar", "difflib", "distutils", "doctest", "inspect", "pdb", "unittest"],
    # comma-separated list of DLLs to exclude
    "dll_excludes": ["VCRUNTIME140.dll"],

    # comma-separated list of packages to include with subpackages
    # "packages": [],
    # if true, use unbuffered binary stdout and stderr
    # "unbuffered": False,
    # list of gen_py generated typelibs to include
    # "typelibs": [],
    # do not automatically include encodings and codecs
    # "ascii": False,
    # do not place Python bytecode files in an archive, put them directly in the file system
    # "skip-archive": False,
    # create and show a module cross reference
    # "xref": False,
    # comma-separated list of modules to include
    # "includes": [],
    # comma-separated list of modules to ignore if they are not found
    # "ignores": "dotblas gnosis.xml.pickle.parsers._cexpat mx.DateTime".split(),
}

# Some options can be overridden by command line options...
setup(
    name = "TileCutter",
    version = config.version,
    author = "André Zanghelini, Timothy Baldock",
    maintainer = "André Zanghelini",
    license = "BSD-3 like",
    url = "https://github.com/An-dz/tilecutter",
    description = "Simutrans Building Editor",
    long_description = "Cut an image into the correct sizes to be used by Simutrans",
    # console based executables
    # console=[],

    # windows subsystem executables (no console)
    windows = [tilecutter],

    # py2exe options
    zipfile = None,
    options = {"py2exe": py2exe_options},

    # distclass = "",
    # script_name = "",
    # script_args = "",
    # options = "",
    # author_email = "",
    # maintainer_email = "",
    # keywords = "",
    # platforms = "",
    # classifiers = "",
    # download_url = "",
    # requires = "",
    # provides = "",
    # obsoletes = "",
)

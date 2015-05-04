from distutils.core import setup
import py2exe

setup(
    windows = [
        {
            "script": "tilecutter.py",
            "icon_resources": [(1, "tilecutter.ico")]
        }
    ],
)
    
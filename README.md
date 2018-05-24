# TileCutter

TileCutter is a tool designed to allow easy creation of multi-tile or multi-view building graphics for use with [Simutrans](https://www.simutrans.com/).

Its primary purpose is to take an image (or set of images) of a building and cut them into the individual paksize tiles used by the game to display the building.

It can output source files (`.dat` and `.png`), a compiled `.pak` file (by integrating with the Simutrans Makeobj utility) or both.

## Dependencies

- [Python 3](https://www.python.org/)
- [wxPython 4](https://wxpython.org/)

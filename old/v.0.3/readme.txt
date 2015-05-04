TileCutter v0.3d - Release Notes
--------------------------------

TileCutter is a building editor tool for use primarily with Simutrans. It is written in Python, and makes use of the wxPython and PIL libraries.

http://www.wxpython.org/
http://www.pythonware.com/products/pil/

This version ought to work a bit better, but as always there are bound to be bugs and I take no responsibility for what may happen as a result of using this software (standard disclaimer, if it eats you not my fault...)

If you find a bug, please tell me about it! You can e-mail me at:

asterix_pop@hotmail.com

Or comment on the forum somewhere... (http://forum.simutrans.com/)

Put "TileCutter" in the subject line, and give a good description of the bug and how it occurs.


Change log
----------

New in 0.3d.1
FIX: Bug in cutting routine moving everything down by one pixel
FIX: Monuments/Curiosities improperly handled in dat output (GUI still a little buggy here, but will fix that in the next major release)

Release 0.3d:
ADD: Export dat file only option added to menu
ADD: Can move cutting mask in paksize increments (use "Fine" control to switch back to pixel-increments)
ADD: Support for "needs_ground" flag
ADD: Can define climates building will appear in
FIX: Input/Output goods for factories now saved correctly
FIX: Level info indicator now translatable
CHANGE: Translation now done via more Simutrans-like system, hopefully compatible with SimuTranslator
ADD: Auto-translation string finding script (TileCutterTranslator) to simplify work of maintaining the base translation file
FIX: Disabled Makeobj-related things (for now)

Release 0.3c:
FIX: .dat image array information now outputted correctly
FIX: Image masking works correctly for upper building tiles
ADD: Now stores a backup copy if an existing .dat file is found


Program usage
-------------

If this is your first time running the program, you will be prompted to select a language, English is currently the only option (if you want to help with translation, please e-mail me or check out the forum!).

After selecting a language you will be presented with the main interface of TileCutter, there is a large blue area where the building graphic appears, a sidebar on the right which lets you set various dimensional properties of the project, and a bottom bar which lets you set filenames.

Buildings can have up to 4 views, you can select which view to edit using the buttons in the top-right of the blue area, to set the number of views your project uses use the "Views" dropdown box, there are three options:

1 - Use only one view for the building
2 - Use a North-South and East-West view
4 - Use a seperate view for each compass direction

1x1 citybuildings can now have multiple rotations so that they face the road. Stations can have two or four rotations also so this feature can be used with them too.

Another important setting is the paksize, this determines the size of tile the image will be cut up into, you can set this to any multiple of 16 between 16 and 240. Changing the paksize will change the size and shape of the red cutting guide displayed over your image (this indicates the area of the image which will be cut out by the program and displayed in the game, nothing outside of the red line will be seen in-game!)

To load an image click the "Browse" button at the bottom of the blue area, locate a file to use and click OK. The image will then appear in the blue area. If this is the first image you've added to the project TileCutter will automatically determine the dimensions of the image. You can use this automatic feature at any time by clicking the "Auto" button underneath the dimension control boxes. To manually adjust the dimensions of the cutting mask, adjust the values in the dimension controls.

NOTE: The dimensions are not just adjusted for the currently selected view, but for all 4! Buildings in Simutrans must be the same shape in all views.

To edit dat file information for your project, select ".dat file options" from the "tools" menu, you can enter all dat file information pertaining to buildings here.

To adjust program preferences, select "preferences" from the "tools" menu, you can change the language for the program here.

To start a new project, select "new project" from the "file" menu, you can also save your project and open a previously saved project from this menu.

To export your project to a .png and .dat image ready for compilation by Makeobj, select "Export Source" from the "File" menu. Exporting direct to makeobj will be supported in the next version! You can also now export only the .dat file by using the relavent option.

Anyway, you should be able to figure the rest out for yourself!


End bit
-------

Planned for the next release: Code cleanup, makeobj integration and some translations! (Hopefully...)

Thanks for using TileCutter, I hope you find it helpful :)

Timothy




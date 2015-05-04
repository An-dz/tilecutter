   ######################
   #  TileCutter v.0.1  #
   ######################
   #       Readme       #
   ######################

1. Introduction

TileCutter is a utility for cutting up images (in .png format) into tiles for display in Simutrans. It also outputs image array information describing the image in a form that Makeobj will understand. The .dat files produced by TileCutter are not directly usable by Makeobj, you need to fill in the rest of the .dat file first, this program only gives you the image array.

I am not a very experienced programmer, so this program may behave in strange and unexpected ways... Please do tell me if it breaks, so I can fix it, contact details are section 4. :)

2. Known Issues

At the moment TileCutter doesn't work very well with asymmetric buildings (specifically ones which are wider than they are long...) this will be fixed in v.0.2 (I hope).

3. Instructions for use

*Important*
TileCutter requires images in .png (Portable Network Graphics) format. Any sort of .png should be ok, TileCutter will always output them in the right format for Makeobj/Simutrans.

This version of the program does not check to see if the filename you specify already exists, and will quite happily overwrite it without warning, so take care.

TileCutter works through the command line, so there are two options for using it. The first is to make a shortcut to the program with the arguments you wish to use included. The second is to open a command prompt window, and navigate to the directory containing the program, then issuing the "tilecutter" command followed by the necessary switches.

Required arguments:

"input filename", "output png filename", "output dat filename", -pakSize

Optional arguments:

-i, -h, -f

(The required arguments have to be in that order, the optional ones can be in any order)

3.a. Arguments

"input filename" must be a valid .png file in the same directory as TileCutter, e.g. "example.png"

"output png filename" is what the output file will be called, and what the image references in the dat file will refer to, e.g. "output.png"

"output dat filename" is the name of the outputted dat file, e.g. "output.dat"

NOTE: You can change the dat file name easily, but if you change the name of the outputted png file the references in the dat file will be broken.

3.b. Switches

-pakSize XX	This specifies the pak size that the program will use, valid values are any multiple of 16 between 16 and 240 inclusive.

-i XX YY	This is the irregular building switch, if your building is not square (i.e. the dimensions are something like 4x5, or 1x3 or something) you have to use this switch when running the program, or the outputted image won't be correct. XX is the number of tiles in the North-South dimension, YY in the East-West dimension (as it would be in-game)

-f X		This switch specifies the orientation, which will be set in the .dat file.

-h X		This is the height override switch, TileCutter by default will try to determine the correct height used for your building automatically, but if you want to override this you can use this switch. X is a value between 1 and 4, specifying the height level of the building.

3.c Example

To run from the command line (for example):

tilecutter inputimage.png outputimage.png outputdat.dat -pakSize 64 -i 4 5 -f 3 -h 3

Will instruct the program to load "inputimage.png", output it to "outputimage.png", write the .dat file information to "outputdat.dat" and use a pak size of 64. Additionally, it specifies that the building has dimensions 4x5, should face West, and overrides the automatic height detection with a value of 3.

This information can be accessed in the program by generally doing something wrong (try typing just tilecutter at the command line)

4. End

I hope you find this tool useful, it'll get better in time I'm sure... Any comments/requests etc. can be directed to me by e-mail:

asterix_pop@hotmail.com

You can also visit the TileCutter website at:

http://simutrans.entropy.me.uk/tilecutter


 - Timothy Baldock


# TileCutter images resource compiler script
#
# Uses wx:img2py to compile a python script with all the image resources used by TileCutter
#

import img2py, os

OUTPUT_FILE = ".." + os.path.sep + "imres.py"

# All .png files in the current directory will be compiled
list = os.listdir(".")
file_list = []

file = open(OUTPUT_FILE, "w")
file.write("")
appen = False

for i in list:
    split = os.path.splitext(i)
    if split[1] == ".png":
        file_list.append(i)
        # Remove the trailing & redundant string "-icon" from the filenames
        name = split[0].replace("-icon","")
        # Convert any "-" in filename to "_"
        name = name.replace("-","_")
        img2py.img2py(i, OUTPUT_FILE, append=appen, imgName=name, icon=True, catalog=True)
        appen = True


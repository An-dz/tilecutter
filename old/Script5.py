filename = "tc_xx.tab"

# Open file & read in contents
f = open(filename)
block = f.read()
f.close()

# Init StringIO and ConfigParser
sio = StringIO.StringIO()
cfgparser = ConfigParser.SafeConfigParser()
# Config, everything within [setup][/setup]
configitems = re.findall("(?=\[setup\]).+(?=\n\[/setup\])", block, re.DOTALL)[0]
configitems_lines = re.split("\n", configitems)
for i in lines:
    sio.write(i + "\n")
sio.flush()
sio.seek(0)
cfgparser.readfp(sio)
sio.close()
# Can now query config items using cfgparser

print cfgparser.has_option("setup", "name") 

# Remove config section from the block
block = re.split("\[/setup\]\n", block, re.DOTALL)[1]
# Then split it up into lines
block_lines = re.split("\n", block)
# Delete all items of block_lines which begin with "#"
block_lines2 = []
for i in range(len(block_lines)):
    if len(block_lines[i]) == 0:
        block_lines2.append(block_lines[i])
    elif block_lines[i][0] != "#":
        block_lines2.append(block_lines[i])
# Then go over the rest, two lines at a time, first line key, second line translation
translation = {}
keys = []
values = []
for i in range(0, len(block_lines2), 2):
    # Populate keys and values lists
    keys.append(block_lines2[i])
    values.append(block_lines2[i+1])
# Make dict from keys
translation.fromkeys(keys)
# Populate dict with values
for i in range(len(values)):
    translation[keys[i]] = values[i]

##print translation

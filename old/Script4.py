import ConfigParser, StringIO

p = ConfigParser.RawConfigParser()

block = ""
b = open("tc_xx.tab")
block += b.read()
b.close()

strings = StringIO.StringIO()

# Use a regex to locate everything within the [setup][/setup] section
s = re.findall("(?=\[setup\]).+(?=\n\[/setup\])", block, re.DOTALL)

block = re.split("\[/setup\]\n", block, re.DOTALL)[1]

print block

lines = re.split("\n", s[0])


print lines
print len(lines)

##print strings.getvalue()

for i in lines:
    strings.write(i + "\n")
##    if lines[i] != "":
##        if i < len(lines)-1:
##            strings.write(lines[i] + "\n")
##        else:
##            strings.write(lines[i])

strings.flush()
strings.seek(0)
p.readfp(strings)

print p.get("setup","name")

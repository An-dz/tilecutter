import os

class pathObject:
    """Contains a path as an array of parts with some methods for analysing them"""
    def __init__(self, pathstring):
        """Take a raw pathstring, normalise it and split it up into an array of parts"""
        path = pathstring
        norm_path = os.path.abspath(pathstring)

        p = path
        self.path_array = []
        # Iterate through the user supplied path, splitting it into sections to store in the array
        while os.path.split(p)[1] != "":
            n = os.path.split(p)
            self.path_array.append(path2(n[1],os.path.exists(p),len(p) - len(n[1])))
            p = os.path.split(p)[0]
    def __getitem__(self, key):
        return self.path_array[key]
    def blah(self):
        return 1
    def __str__(self):
        a = ""
        for k in range(len(self.path_array)):
            a = a + "<[" + str(k) + "]\"" + self.path_array[k].text + "\"," + str(self.path_array[k].offset) + "," + str(self.path_array[k].length) + "," + str(self.path_array[k].exists) + ">, "
        return a

class path2:
    def __init__(self,text,exists,offset):
        self.text = text            # Textual content of this section of the path
        self.length = len(text)     # Length of this section of the path
        self.offset = offset        # Offset from start of string
        self.exists = exists        # Does this path section exist in the filesystem
    def __len__(self):
        return self.length
    def __str__(self):
        return self.text
    def exists(self):
        return self.exists



a = pathObject("old\\output/blah/output.dat")

print len(a[1])
print a






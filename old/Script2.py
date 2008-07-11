import sys, os

def split(p1, p2=None):
    """Split a path into an array, index[0] being the first path section, index[len-1] being the last
    Optionally takes a second path which is joined with the first for existence checks, to allow for
    checking existence of relative paths"""
    if os.path.split(p)[1] == "":
        # Check to make sure there isn't a trailing slash
        if os.path.split(os.path.split(p)[0])[1] != "":
            p = os.path.split(p)[0]
    a = []
    while os.path.split(p)[1] != "":
        n = os.path.split(p)
        # Add at front, text,   offset,             length,     exists or not,      File or Directory?
        a.insert(0,    [n[1],  len(p)-len(n[1]),   len(n[1]),  os.path.exists(p)])#, existsAsType(p)])
        p = n[0]
    print a
    return a

def joinPaths(p1,p2):
    """Join p2 to p1, accounting for end cases (is directory, is file etc.)"""

def existingPath(p):
    """Take a path and return the largest section of this path that exists
    on the filesystem"""
    if os.path.split(p)[1] == "":
        # Check to make sure there isn't a trailing slash
        if os.path.split(os.path.split(p)[0])[1] != "":
            p = os.path.split(p)[0]
    while not os.path.exists(p):
        p = os.path.split(p)[0]
    return p

def compare(p1,p2):
    """Compare two absolute paths, returning either a relative path from p1 to p2, or p1 if no relative path exists"""
    # First check that both paths are on the same drive, if drives exist
    if os.path.splitdrive(p1)[0] != os.path.splitdrive(p2)[0]:
        return p1
    p1s = split(os.path.normpath(p1))
    p2s = split(os.path.normpath(p2))
    k = 0
    while p1s[k][0] == p2s[k][0]:
        k += 1
    # Number of /../'s is length of p2s minus k (number of sections which match, but remember this will be one more
    # than the number which match, which is what we want as the length is one more than we need anyway
    p3 = ""
    # If p2's last component is a file, need to subtract one more to give correct path
    e = 1
    for a in range(len(p2s)-k-e):
        p3 = os.path.join(p3, "..")
    # Then just add on all of the remaining parts of p1s past the sections which match
    for a in range(k,len(p1s)):
        p3 = os.path.join(p3, p1s[a][0])
    return p3


path1 = "C:\\Documents and Settings\\Timothy Baldock\\My Documents\\Programming\\TileCutter\\v.0.5\\dino.png"

path2 = "C:\\Documents and Settings\\Timothy Baldock\\My Documents\\Blah\\dino.png"

print compare(path1,path2)


print existingPath(path2)






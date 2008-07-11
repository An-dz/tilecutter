
# ***************** Catalog starts here *******************

catalog = {}
index = []

class ImageClass: pass

#----------------------------------------------------------------------
def getbackimageData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd1 \xcc\xc1\x04$\
\xffv\x16k\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9s<]\x1cC4&\
\xf6^\xdc\xc8u\xc8A\xa0\xe5\xa1\xbd\x90\x8eY\xc2\xd4(n\xe9\xec\xfb\xffmkZ\
\xb47\x85*\x04s&'vx\xf6\xccx\xd8\x15\xfdcGr\xf9\xea\xa4\xcd\xca\xed\xb6\x1c+\
\x96\xdf\x9e\xea\xd6\xd1\xb2\xe4\xce1\x7f?_\xe6/\x87\x1d6v\xcb\xf2\x9d\xa9\
\xb0\xaax\xb0\xad\xf4\x08\x83\xac\xc8l\xd3O\x1a\xf7\xae>\xc9bpd\xf8Q\xa4&\
\xfc\xb4L\xde\xab\x95\xc9\xc1\xe9\xd7]w%\x91\xdc?3\xbdw\xcev\xd9\xf9\xf7\xd2\
q\xdf\x12\xe3Y\xbb'\xeaM\xbep\xdb}\xf6\xcf9\xe1\x8fv\xdeI7\xbd\xff~\xe5\xaa/\
\xaa\xf7*\x19?\xb9\xc6\\7\xe6\xbf\x9d\x0bt'\x83\xa7\xab\x9f\xcb:\xa7\x84&\
\x00r\x00[\xf4" )

def getbackimageBitmap():
    return BitmapFromImage(getbackimageImage())

def getbackimageImage():
    stream = cStringIO.StringIO(getbackimageData())
    return ImageFromStream(stream)

def getbackimageIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getbackimageBitmap())
    return icon

index.append('backimage')
catalog['backimage'] = ImageClass()
catalog['backimage'].getData = getbackimageData
catalog['backimage'].getImage = getbackimageImage
catalog['backimage'].getBitmap = getbackimageBitmap
catalog['backimage'].getIcon = getbackimageIcon


#----------------------------------------------------------------------
def getcenterData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\xdc@\xcc\xce\
\xc1\x04$\x03y\x14@\x12\xcc\xc5N\x9e!\x1c\x1c\x1c\xb7\x1f\xfa?\x00r\xad<]\
\x1cC8f&\xd7\xfc\xfb\xbf_E\xf9\xf1\xe7\xff\xff%\r\x18\\\xe6LlldT\xea]\xc3wnZ\
JJJ\xc3\xea\x03\xaeF\x89R}l\x1c\xb7\x0fu<\x0b\xf21\xeb\xd2\xdfP\xc5\xc5\xa0\
\xccfm\x90uL\xe93\xd0\x14\x06OW?\x97uN\tM\x00r\xfe'R" )

def getcenterBitmap():
    return BitmapFromImage(getcenterImage())

def getcenterImage():
    stream = cStringIO.StringIO(getcenterData())
    return ImageFromStream(stream)

def getcenterIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getcenterBitmap())
    return icon

index.append('center')
catalog['center'] = ImageClass()
catalog['center'].getData = getcenterData
catalog['center'].getImage = getcenterImage
catalog['center'].getBitmap = getcenterBitmap
catalog['center'].getIcon = getcenterIcon


#----------------------------------------------------------------------
def getdownData():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\xec@\xcc\xc2\
\xc1\x04$\xcf.\xd9\xa4\x05\xa4\x98\x8b\x9d<C888n?\xf4\x7f\x00\xe4Jy\xba8\x86\
p\xccLN8\xc05\xef\xff\xff~\xcdC-j\x8c\x89\xc6\x8a\xc5\x0f.1\xd8v\x08&\xcf\
\x0f\xb8\xf6\x0b\xa8\x8a\xc1\xd3\xd5\xcfe\x9dSB\x13\x00N\xcc\x1b\x87' )

def getdownBitmap():
    return BitmapFromImage(getdownImage())

def getdownImage():
    stream = cStringIO.StringIO(getdownData())
    return ImageFromStream(stream)

def getdownIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getdownBitmap())
    return icon

index.append('down')
catalog['down'] = ImageClass()
catalog['down'].getData = getdownData
catalog['down'].getImage = getdownImage
catalog['down'].getBitmap = getdownBitmap
catalog['down'].getIcon = getdownIcon


#----------------------------------------------------------------------
def getdown_leftData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2l \xcc\xc1\x04$\
\xf3\xd7U\xc8\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9J\x9e.\
\x8e!\x1c3\x93S\x12\x12*\xfe\xfd\xb7g\x16Jh\t8\xb1\xa8\xa7@,f\x8a`$\xf7,\xce\
\nW\xc6uf|u\x07\x8f\xc46\x03U3x\xba\xfa\xb9\xacsJh\x02\x00\xe8J\x1cr" )

def getdown_leftBitmap():
    return BitmapFromImage(getdown_leftImage())

def getdown_leftImage():
    stream = cStringIO.StringIO(getdown_leftData())
    return ImageFromStream(stream)

def getdown_leftIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getdown_leftBitmap())
    return icon

index.append('down_left')
catalog['down_left'] = ImageClass()
catalog['down_left'].getData = getdown_leftData
catalog['down_left'].getImage = getdown_leftImage
catalog['down_left'].getBitmap = getdown_leftBitmap
catalog['down_left'].getIcon = getdown_leftIcon


#----------------------------------------------------------------------
def getdown_rightData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2l \xcc\xc1\x04$\
\xf3\xd7U\xc8\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9j\x9e.\
\x8e!\x1c3\x93k\xfe\xfd\xb7g\x16\x9a\x90\x92\x92\xe2\xf4\xd8\xd8\xc0\xc0`\
\xe1GA\xa7\x02;f \x98\x15y\x83\x91\xe1\x9c4\x9b\x9dAm\xa1\x16P\x07\x83\xa7\
\xab\x9f\xcb:\xa7\x84&\x000H\x1b\x8f" )

def getdown_rightBitmap():
    return BitmapFromImage(getdown_rightImage())

def getdown_rightImage():
    stream = cStringIO.StringIO(getdown_rightData())
    return ImageFromStream(stream)

def getdown_rightIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getdown_rightBitmap())
    return icon

index.append('down_right')
catalog['down_right'] = ImageClass()
catalog['down_right'].getData = getdown_rightData
catalog['down_right'].getImage = getdown_rightImage
catalog['down_right'].getBitmap = getdown_rightBitmap
catalog['down_right'].getIcon = getdown_rightIcon


#----------------------------------------------------------------------
def getdown2Data():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\xec@\xcc\xc1\
\xc1\x04$w\xa5\x15\x05\x02)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\
\xb9\xb2\x9e.\x8e!\x1c3\x93\x13\x0ep\xcd\xfb\xff\xbf_\xf3P\x8b\x1ac\xa2\xb1b\
\xb1\xc1\xd7\xc0\x9b1\x0c\xa5RJG/\xac\xdc\x9c\x01T\xc8\xe0\xe9\xea\xe7\xb2\
\xce)\xa1\t\x00\x88Q\x1c/" )

def getdown2Bitmap():
    return BitmapFromImage(getdown2Image())

def getdown2Image():
    stream = cStringIO.StringIO(getdown2Data())
    return ImageFromStream(stream)

def getdown2Icon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getdown2Bitmap())
    return icon

index.append('down2')
catalog['down2'] = ImageClass()
catalog['down2'].getData = getdown2Data
catalog['down2'].getImage = getdown2Image
catalog['down2'].getBitmap = getdown2Bitmap
catalog['down2'].getIcon = getdown2Icon


#----------------------------------------------------------------------
def geteastData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd1 \xcc\xc1\x04$\
\xffv\x16k\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9\xd5\x9e.\
\x8e!\x1a\x13{'^\xe4=\xa0\xc0\xe1r\xb4\x84S\xfd\x85D\xaa\x89\xec\xe2\xdbs\
\x92-\x1a\x93/\xf0\x0by\xadU\x8b\xfba\xf0\xc1\xe2\xbcG\xacJ\xce\x8b\x19e\xc2\
\x13\xe7^\xcd8w\xf3\x86Hx\x8c\xd2\xa7u\xbb\xeb\xbc\xcf\x9d)Q\xbc%\xba6,?\xed\
\xeb\xb3\xd7J\x0c3*\x17\x84\x96k>\xd6b\x98\xcbx\xc1\xef\\\xe4L\xff}\x9fw\xed\
\xf2X=u\xa63\x07\x97\xef\xa2\x1f\x9f.\xbc\xf8^\xbf\xa6\xd3\xec\xffwF\xb6\xc7\
\x19b\xabj\n|\x80\xce`\xf0t\xf5sY\xe7\x94\xd0\x04\x00\xca\xd5L\x0f" )

def geteastBitmap():
    return BitmapFromImage(geteastImage())

def geteastImage():
    stream = cStringIO.StringIO(geteastData())
    return ImageFromStream(stream)

def geteastIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(geteastBitmap())
    return icon

index.append('east')
catalog['east'] = ImageClass()
catalog['east'].getData = geteastData
catalog['east'].getImage = geteastImage
catalog['east'].getBitmap = geteastBitmap
catalog['east'].getIcon = geteastIcon


#----------------------------------------------------------------------
def getfrontimageData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd1 \xcc\xc1\x04$\
\xffv\x16k\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9\xab<]\x1cC\
4&\xf6N\\\xc8w(\x80\xc7\xd5\xff\xe4i\x97\xe9\x0b\xee\x1d\xe1\x91:\x7f\xff\
\x83j\x8d\x82\xd4\xe9/g\x8c\xaf^\xb7c\x896;\xe6\xb4\xe2\xf5\xd9\xcc\xea\xdbQ\
+\xa7\xda?\xda\xb0Zms\xca\xb7n\xebmo/\x9eq\x9c}\xca\xf4a\x03\x0b\x0b\xc7,\
\xde\xe9\xbb\xfc\x04\xed\xbcsK\x15\x99\xd8\xb4\x9f\xef:s\xf6\xddr^\x96\x94\
\x13_\x9a\xdf\xfe\x88^P\x9eR\xf0\xab\xbd\xf6\xedF\xc3\xfdB\xf6\x16\xad1\xfb\
\x9el\x0cYf\xea\xae\xf0\xe4f\xab\x00\x0bKO\xb1\xfd\xd9\xed\x15q\n\x01\x19JLn\
\xa7\xb62\x85e\xf9\xa65\xa5\xd5%\xd4o_y\xd3c\xa7\xef\xa2\xbf?\xef\x8b\xb7\
\xd8{\xc8\x94\xda~)\x02\xba\x9a\xc1\xd3\xd5\xcfe\x9dSB\x13\x00\xce\xfac%" )

def getfrontimageBitmap():
    return BitmapFromImage(getfrontimageImage())

def getfrontimageImage():
    stream = cStringIO.StringIO(getfrontimageData())
    return ImageFromStream(stream)

def getfrontimageIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getfrontimageBitmap())
    return icon

index.append('frontimage')
catalog['frontimage'] = ImageClass()
catalog['frontimage'].getData = getfrontimageData
catalog['frontimage'].getImage = getfrontimageImage
catalog['frontimage'].getBitmap = getfrontimageBitmap
catalog['frontimage'].getIcon = getfrontimageIcon


#----------------------------------------------------------------------
def getleftData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2,@\xcc\xce\xc1\
\x04$\x17\xb0W\xb7\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9\
\xea\x9e.\x8e!\x1c3\x93k\xfe\xfd\xb7g\x06\x81f\x15ee\xe19G\x0f\x1c8\xc00\xfd\
 \xc3\t#\x9f\x135j)\x95\x0c\xf5\xb3\xf9\xb6/\x99%$\x05\xd4\xc2\xe0\xe9\xea\
\xe7\xb2\xce)\xa1\t\x00b\x0e\x1d\xc9" )

def getleftBitmap():
    return BitmapFromImage(getleftImage())

def getleftImage():
    stream = cStringIO.StringIO(getleftData())
    return ImageFromStream(stream)

def getleftIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getleftBitmap())
    return icon

index.append('left')
catalog['left'] = ImageClass()
catalog['left'].getData = getleftData
catalog['left'].getImage = getleftImage
catalog['left'].getBitmap = getleftBitmap
catalog['left'].getIcon = getleftIcon


#----------------------------------------------------------------------
def getleft2Data():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\x1c@\xcc\xce\
\xc1\x04$wY\xcf\xe6\x04R\xcc\xc5N\x9e!\x1c\x1c\x1c\xb7\x1f\xfa?\x00ru<]\x1cC\
8f&\xd7\xfc\xfbo\xcf\x0c\x02\xcd*\xca\xcaF\xb39\xcf%50jH\xaf\xe3\xea\xed\x95\
~p\xe9`\x8bw\x1f\xe7t;\x86\xa0V\xd9\xb4\xb6\xc5lS\x80\xfa\x18<]\xfd\\\xd69%4\
\x01\x00\xcb\x05\x1eb' )

def getleft2Bitmap():
    return BitmapFromImage(getleft2Image())

def getleft2Image():
    stream = cStringIO.StringIO(getleft2Data())
    return ImageFromStream(stream)

def getleft2Icon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getleft2Bitmap())
    return icon

index.append('left2')
catalog['left2'] = ImageClass()
catalog['left2'].getData = getleft2Data
catalog['left2'].getImage = getleft2Image
catalog['left2'].getBitmap = getleft2Bitmap
catalog['left2'].getIcon = getleft2Icon


#----------------------------------------------------------------------
def getnorthData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd1 \xcc\xc1\x04$\
\xffv\x16k\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9\xb5\x9e.\
\x8e!\x1a\x13\xa7N\xb8\xc8\xdb`\xc0\xe1\xd2\x7fL\xd5\xaa1\xf9\xc6\xc5\x17\
\x12y\xc5}\x0fYd\x99\xed\r\x8e\xdc\xc8\xfar\x88\xbd\xf5:\xb7\xc2Y\x1e\xf9)\
\x0c)\x13\xb7\x86\xd5\xa7O4\x94\xa8[\xf5\xaa\xd2\xf8u2\xd7\xaf\x8b\x9c\x0c\
\x06\xb1\xbd\xf1\x17L\xe6,\x9c\xceSm\xfe8mZ\xd5\t\xe9UV\xf3\xf4\xb7\xe4Gk\
\xb26,~\xde\xfe\xfa\x93\x8a\xac\xeaK\xd1\xf6Y\x92\xf3:8\xf6\xaf>b\xe9q\xee\
\xf4\xa7\xfc\xfbq\xec\xbc\xdf*o2m{\xb0\x13\xe8\x10\x06OW?\x97uN\tM\x00\x8cTI\
\xe0" )

def getnorthBitmap():
    return BitmapFromImage(getnorthImage())

def getnorthImage():
    stream = cStringIO.StringIO(getnorthData())
    return ImageFromStream(stream)

def getnorthIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getnorthBitmap())
    return icon

index.append('north')
catalog['north'] = ImageClass()
catalog['north'].getData = getnorthData
catalog['north'].getImage = getnorthImage
catalog['north'].getBitmap = getnorthBitmap
catalog['north'].getIcon = getnorthIcon


#----------------------------------------------------------------------
def getreloadfileData():
    return zlib.decompress(
'x\xda\x01\x8b\x01t\xfe\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\r\x00\
\x00\x00\r\x08\x02\x00\x00\x00\xfd\x89s+\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\
\xe1O\xe0\x00\x00\x01CIDAT(\x91u\x90=/Cq\x14\xc6\x7f\xff\xdb\xab\xd5\xd2\xaa\
\xa6\xa4\xb7*\xe8\xa8\xdekD\xe2.\xfd\x02b\xf1\x11,\x16\x16\xb1\x1a0H\x18,\
\x16\x9bIb\xe0\x03t\xef\xd2\x94\x18$\x0c\xf5oL\x8d\x976\xbdm\x1d\xc3\xa5n\
\x82\'\'\'99\xcfy\xf2\x9c\x07-\xf2\xbb\x0c_"\x95\xb4a"\xe8\xcf\xeel\x9fi\x11\
\x13\xc8D\x17K\xd5<\x00db\xb3u\xa7Rni\xbea\xa9\xe9A+\x80\x16\t\x99v8\x90\xd3\
"\xf1\xa8\xfd\xa7\xbc?\x902\x81f\xcb\x1f\xeeN[J\x01n\xf7B\x8b4\x1d1\x01\xf8x\
}\xab\x01\x02\x88\xfcP\xd4\xd7Q$\x121\x00\x9f\xaf^\xe3\x81\xff\xb1\xb9\xb5\
\xa1\xf4\xb7\x80\xa5\x94\xfcb(p\t\x06p\xba{\xd2Y\xdc\x16\x0bn\x8d\x0e\xdb\
\x8a\xec`d\xcdR\xcbc\xe6\x92\x01\xec\xef\x1dz5\xc6\'\xe7\x80\xeb\xab\x83\xf4\
\xc8P\xfd]\x85\x18m\xb7\x83\x06\xf0\xf2\xf2\xe6\xfe\xe5\xba\xbe)\x16\xdc\x83\
\xfb\xc7K\xa7\xfd\x1e\xee\r\x81a\x02]~\xd5\x89\xc0\x9bK<j7\xaa\x17\xb5f\xae\
\xcbl\xa2E\x8e\x8e\xcfa\xca\x1bl\xb0\'\x11\xeb\x9f\xe9\x8c\xb1\xbe\x05\x13XY\
_}\xd6\x8dt`\xbe\xee4R\xc9\x81\xa7\xca]\xb9\xad=\x86)U\xf3\x9f\t\xf2\xad*z8/\
\xbe\x00\x00\x00\x00IEND\xaeB`\x82\xf4n\xae\xd8' )

def getreloadfileBitmap():
    return BitmapFromImage(getreloadfileImage())

def getreloadfileImage():
    stream = cStringIO.StringIO(getreloadfileData())
    return ImageFromStream(stream)

def getreloadfileIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getreloadfileBitmap())
    return icon

index.append('reloadfile')
catalog['reloadfile'] = ImageClass()
catalog['reloadfile'].getData = getreloadfileData
catalog['reloadfile'].getImage = getreloadfileImage
catalog['reloadfile'].getBitmap = getreloadfileBitmap
catalog['reloadfile'].getIcon = getreloadfileIcon


#----------------------------------------------------------------------
def getrightData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2,@\xcc\xce\xc1\
\x04$\x17\xb0W\xb7\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9*\
\x9e.\x8e!\x1c3\x93S\x12\x12*\xfe\xfd\xb7g\x06\x03\xe5\x96\xa6\xcf\x92\x1b>\
\x07\xa6\x04|1PZ\xcd\xc6\xf0\xe7\xa1`\xb2\xd4\x9a_/\x80\xea\x19<]\xfd\\\xd69\
%4\x01\x00\x16)\x1d\xe7" )

def getrightBitmap():
    return BitmapFromImage(getrightImage())

def getrightImage():
    stream = cStringIO.StringIO(getrightData())
    return ImageFromStream(stream)

def getrightIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getrightBitmap())
    return icon

index.append('right')
catalog['right'] = ImageClass()
catalog['right'].getData = getrightData
catalog['right'].getImage = getrightImage
catalog['right'].getBitmap = getrightBitmap
catalog['right'].getIcon = getrightIcon


#----------------------------------------------------------------------
def getright2Data():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\x1c@\xcc\xce\
\xc1\x04$wY\xcf\xe6\x04R\xcc\xc5N\x9e!\x1c\x1c\x1c\xb7\x1f\xfa?\x00r\r=]\x1c\
C8f&\xa7$$T\xfc\xfbo\xcf\x0c\x02\xcd*\xca\xcas\xce\xb2<4>\xc0`$\xcd\xf5 \xeb\
\xe2\x8d\x1d\x8c\xb3\xf8\xd4b\x9e\x19<4\x92e8)*\xeb\x1de\xc6~\x17\xa8\x99\
\xc1\xd3\xd5\xcfe\x9dSB\x13\x00\x8bl s' )

def getright2Bitmap():
    return BitmapFromImage(getright2Image())

def getright2Image():
    stream = cStringIO.StringIO(getright2Data())
    return ImageFromStream(stream)

def getright2Icon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getright2Bitmap())
    return icon

index.append('right2')
catalog['right2'] = ImageClass()
catalog['right2'].getData = getright2Data
catalog['right2'].getImage = getright2Image
catalog['right2'].getBitmap = getright2Bitmap
catalog['right2'].getIcon = getright2Icon


#----------------------------------------------------------------------
def getsameforallData():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd1 \xcc\xc1\x04$\
\xffv\x16k\x03)\xe6b\'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb93=]\x1cC4&\
\x96\x06\x1e\xe4=\xac\xc0\xb3\xa7{\x13\x8b\xb2\x89P\x7f\x1a\x93[\xb9\xd8\x02\
~\x95U~\x07$\xde\x1d\xceRXf\xa9xz\xc1\xe7\x9f~\x02\xe6\x19\xab\x1e\x9722\xbc\
\xe0p`\xac\xe9S\x9e\xd0h"W\xbf\xc7\xce\x8bi\xc1K\xd6"\x91k/c\xbe\x99]\xbd\
\xba+*\xee\xf9k\xb1\xf9\xd7:<\xbc<]v\xc5\xe9J:\xe8\xee\x9c\x96S\xc5w\xfa\xe5\
\xa5\x15\xb5_\xa4z\x9f\xf5Mn\xe8\xbeV\xb9\xcej\xcdf\xd1\xc3\xd5\x1b>v\xfc.:\
\xce\xbc\xe1\xe8\xde\xe7\x19\xabX\xb2N\xae\xfb\x95\xe2{\xb5\xf6i|\r#sc\xbaWB\
\xe75S\xa0#\x19<]\xfd\\\xd69%4\x01\x00H\x93Xs' )

def getsameforallBitmap():
    return BitmapFromImage(getsameforallImage())

def getsameforallImage():
    stream = cStringIO.StringIO(getsameforallData())
    return ImageFromStream(stream)

def getsameforallIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getsameforallBitmap())
    return icon

index.append('sameforall')
catalog['sameforall'] = ImageClass()
catalog['sameforall'].getData = getsameforallData
catalog['sameforall'].getImage = getsameforallImage
catalog['sameforall'].getBitmap = getsameforallBitmap
catalog['sameforall'].getIcon = getsameforallIcon


#----------------------------------------------------------------------
def getsouthData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd1 \xcc\xc1\x04$\
\xffv\x16k\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9\xd5\x9e.\
\x8e!\x1a\x13{'\xde\xe5=\xa0\xc0\xd1rpG\x8bp\t\x8f\xac\xef\xf1\x02i\x99\xc5@\
\xd6\xaf\x82c\x19\xf5!E\x9cj2\xf2\x02?\x83\x96\xf6n\xf0\xe8\x93\xec\xdfo\xc6\
}yR\x94\xec\x03\xdf;\xcc\x99L\xdb\xacO\x0bNt\x94\xac\xbar.H\xc6X\xa3\xad\xa3\
\xc8k~\x9f@S\xc7\x95\xba%\x12\xca\x13\x94\x98\xb4e|\x97\x19\x16y\xd9>\xfeP'q\
q\xfd\xd5\x15\xf9\x1f\x97\xdez77f\xef?\xce#\xbc\x89S\x8b\xaf\xbf\xfe\x95\xff\
\x17\xe8\x0c\x06OW?\x97uN\tM\x00\xf2iGv" )

def getsouthBitmap():
    return BitmapFromImage(getsouthImage())

def getsouthImage():
    stream = cStringIO.StringIO(getsouthData())
    return ImageFromStream(stream)

def getsouthIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getsouthBitmap())
    return icon

index.append('south')
catalog['south'] = ImageClass()
catalog['south'].getData = getsouthData
catalog['south'].getImage = getsouthImage
catalog['south'].getBitmap = getsouthBitmap
catalog['south'].getIcon = getsouthIcon


#----------------------------------------------------------------------
def getsummerData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd1 \xcc\xc1\x04$\
\xffv\x16k\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9\xb3=]\x1cC\
4&\xf6\x06n\x14<\xac p\xb9\xf8\xceE\xa7\xe9\xbc\x12\x07\xe5\x0e/6j\xb3e\x12V\
\xb9{y\xd7/\x11\x7f\x83\x07O\xf4V}\x99\xf4\xe0\xa2\xa3\xbf`\x8f\x05\x7f\xd1i\
\x9dYu\x1c3\x19l\xfe\x1c}\x1e\x13<\xd5G\x99!\xabz\xf5\x93\xedU\xce\x9e\x0c\
\x16a\xd7\xf9\xb4\xff\xb0\xad\x91\xe7\x9b\xb2D\xcc\xdd\xf0\xfaB;\x16\x86\xd5\
\xf7\xd6\xae\xb3\xe5\xbf\xd4\xfe\xdf\xe9\xc4\x17\xad\ry\x82\xfb\xb6\xbe>\x18\
8\xe7\xdb\xda\x85\x93\x1a\xf6r\xbf\x89r\xbd[\xff\xfbZ\xcc\x89#\x81\xcb\xde\
\xae\xca\xb8b\xb2R\xfd\xb2\xc5\x9b\xdc\x1f\xbf\xf6\xe7;\x14\x04.g]\xf3B\r\
\xe8L\x06OW?\x97uN\tM\x00O6\\`" )

def getsummerBitmap():
    return BitmapFromImage(getsummerImage())

def getsummerImage():
    stream = cStringIO.StringIO(getsummerData())
    return ImageFromStream(stream)

def getsummerIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getsummerBitmap())
    return icon

index.append('summer')
catalog['summer'] = ImageClass()
catalog['summer'].getData = getsummerData
catalog['summer'].getImage = getsummerImage
catalog['summer'].getBitmap = getsummerBitmap
catalog['summer'].getIcon = getsummerIcon


#----------------------------------------------------------------------
def getupData():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\xec@\xcc\xc2\
\xc1\x04$\xcf.\xd9\xa4\x05\xa4\x98\x8b\x9d<C888n?\xf4\x7f\x00\xe4\xaay\xba8\
\x86p\xccL\xae\xf9\xf7\xdf\x9e\x19\x04\x9aU\x94\x95\xe7\x9ce\x11o\x9a\xcc\
\x03\x04\x05\x95\x16\x07D\x1a\x99\x18\x16\xcbr\xbf\xf4\xf6\xf9 \t\xd4\xc1\
\xe0\xe9\xea\xe7\xb2\xce)\xa1\t\x00\x1b\xdd\x1b\x1f' )

def getupBitmap():
    return BitmapFromImage(getupImage())

def getupImage():
    stream = cStringIO.StringIO(getupData())
    return ImageFromStream(stream)

def getupIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getupBitmap())
    return icon

index.append('up')
catalog['up'] = ImageClass()
catalog['up'].getData = getupData
catalog['up'].getImage = getupImage
catalog['up'].getBitmap = getupBitmap
catalog['up'].getIcon = getupIcon


#----------------------------------------------------------------------
def getup_leftData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2l \xcc\xc1\x04$\
\xf3\xd7U\xc8\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9J\x9e.\
\x8e!\x1c3\x93\x13\x148\xe6\xfd\xff\x7f\xbe\xe3XzBB\x82\xcbc\xe5\x96\x075+\
\x04\x8c\xe67622\xcc\x9a\xc2W\xf7\xf3\xae\x89\x0cP5\x83\xa7\xab\x9f\xcb:\xa7\
\x84&\x00/\xf5\x1e\x98" )

def getup_leftBitmap():
    return BitmapFromImage(getup_leftImage())

def getup_leftImage():
    stream = cStringIO.StringIO(getup_leftData())
    return ImageFromStream(stream)

def getup_leftIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getup_leftBitmap())
    return icon

index.append('up_left')
catalog['up_left'] = ImageClass()
catalog['up_left'].getData = getup_leftData
catalog['up_left'].getImage = getup_leftImage
catalog['up_left'].getBitmap = getup_leftBitmap
catalog['up_left'].getIcon = getup_leftIcon


#----------------------------------------------------------------------
def getup_rightData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2l \xcc\xc1\x04$\
\xf3\xd7U\xc8\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9\xf2\x9e\
.\x8e!\x1c3\x93\x13\x0e\xb0\x9c\xff\xff\xdf]8\xf1\x90H\xea\xa1\x90\xd3-\x99L\
\xc2\x9b\xc4:4\x18\x8e\xed\xe5k\xea\xd8\xb9\x0b\xa4\x94\xc1\xd3\xd5\xcfe\x9d\
SB\x13\x00\xc48\x1dg" )

def getup_rightBitmap():
    return BitmapFromImage(getup_rightImage())

def getup_rightImage():
    stream = cStringIO.StringIO(getup_rightData())
    return ImageFromStream(stream)

def getup_rightIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getup_rightBitmap())
    return icon

index.append('up_right')
catalog['up_right'] = ImageClass()
catalog['up_right'].getData = getup_rightData
catalog['up_right'].getImage = getup_rightImage
catalog['up_right'].getBitmap = getup_rightBitmap
catalog['up_right'].getIcon = getup_rightIcon


#----------------------------------------------------------------------
def getup2Data():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\xec@\xcc\xc1\
\xc1\x04$w\xa5\x15\x05\x02)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\
\xb9Z\x9e.\x8e!\x1c3\x93k\xfe\xfd\xb7g\x06\x81f\x15e\xe59gY\xc4\x9b&\xf3\x00\
AA\xa5\xc5\x01\x91F&7\xa9\x99\xdc\x0cq\xae\xe2\x17'h/|\x01\xd4\xc5\xe0\xe9\
\xea\xe7\xb2\xce)\xa1\t\x00l\x1d\x1c<" )

def getup2Bitmap():
    return BitmapFromImage(getup2Image())

def getup2Image():
    stream = cStringIO.StringIO(getup2Data())
    return ImageFromStream(stream)

def getup2Icon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getup2Bitmap())
    return icon

index.append('up2')
catalog['up2'] = ImageClass()
catalog['up2'].getData = getup2Data
catalog['up2'].getImage = getup2Image
catalog['up2'].getBitmap = getup2Bitmap
catalog['up2'].getIcon = getup2Icon


#----------------------------------------------------------------------
def getwestData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd1 \xcc\xc1\x04$\
\xffv\x16k\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9\xb9\x9e.\
\x8e!\x1a\x13{'^\xe4=\xa0\xc0\xe1\xd2\x9f\xf7\xd0\xac\xafl\xf1C\x89\xb9\x07\
\x0c\xd7\xc9\x9b\\\x0bI\xf2\xe6p\xacm\x99\x9e\x11{\xa8\xdf\xe2\xd2\xed\xa4o\
\xaf\x8a\xf3\x96\x96\xdf\xf9\x1e7\xe9hN\x08\xc3\x8b\xa0Y*\xeeo'\x95f~\xeb8\
\xd9\xbf\xd7p.\xf71\xe6\x93\xb7\x99\x0b\xbe\x87>~\xf8\xe8\xcd;\xcd\xde\xc8\
\xb2'^\xb7\x9f\xdd?w-k\xed\xc3m\x8f\x9f\xed`\xd0\x9b5\xf1\x8a\xf7\x01\xbd\
\x17@\x8b\x19<]\xfd\\\xd69%4\x01\x00\x1b\x85K\x85" )

def getwestBitmap():
    return BitmapFromImage(getwestImage())

def getwestImage():
    stream = cStringIO.StringIO(getwestData())
    return ImageFromStream(stream)

def getwestIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getwestBitmap())
    return icon

index.append('west')
catalog['west'] = ImageClass()
catalog['west'].getData = getwestData
catalog['west'].getImage = getwestImage
catalog['west'].getBitmap = getwestBitmap
catalog['west'].getIcon = getwestIcon


#----------------------------------------------------------------------
def getwinterData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd1 \xcc\xc1\x04$\
\xffv\x16k\x03)\xe6b'\xcf\x10\x0e\x0e\x8e\xdb\x0f\xfd\x1f\x00\xb9U\x9e.\x8e!\
\x1a\x13{\x03\r\xb9\x8e\x18\xf0\x04\x9fv\x9c\x7fI?\xe5\xf5u\xd3_\xea\x92\xf9\
W\x9f\xf1\xb5\xcdy\xbd-\xc6\xc5\xc0I\xcdKg\xf1\xee\xe7\xceAB'\x17-\xde\xed\
\xee\x1c\xf4\xc1\xe1\xa2=\xc3\x995[\xd3\xd2\x18\x18\xee\xfc\xac\x93\x11\xdf\
\xbf\xa2qM\xc9w\xd1\x03\xe5\xb7\xbb\xb2\x9f]t\xdd\xf7\xfd\x99{\xd1\xc4\x16\
\xce5\x8f\x17\x062\x87\xcao\xbck/\xf0\xc8\xb9\xae\xfe\x99\xee\xe4g\xbfN\x17\
\x15\xc9\xcf\xb8\xf3\x9e\xb3\xc6,\xa4\x8fY\xf0\xe1\x13\xa0+\x18<]\xfd\\\xd69\
%4\x01\x00\xdcAL\x18" )

def getwinterBitmap():
    return BitmapFromImage(getwinterImage())

def getwinterImage():
    stream = cStringIO.StringIO(getwinterData())
    return ImageFromStream(stream)

def getwinterIcon():
    icon = EmptyIcon()
    icon.CopyFromBitmap(getwinterBitmap())
    return icon

index.append('winter')
catalog['winter'] = ImageClass()
catalog['winter'].getData = getwinterData
catalog['winter'].getImage = getwinterImage
catalog['winter'].getBitmap = getwinterBitmap
catalog['winter'].getIcon = getwinterIcon



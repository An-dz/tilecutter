# coding: UTF-8

import codecs

# Codec for converting unix-style newlines to windows-style ones
class Codec(codecs.Codec):
    def encode(self, input, errors="strict"):
        return input.replace("\n", "\r\n"), len(input)

    def decode(self, input, errors="strict"):
        return input.replace("\n", "\r\n"), len(input)

class StreamWriter(Codec, codecs.StreamWriter): pass
class StreamReader(Codec, codecs.StreamWriter): pass

def getregentry(dec=None):
    return (Codec().encode,Codec().decode,StreamReader,StreamWriter)

codecs.register(getregentry)


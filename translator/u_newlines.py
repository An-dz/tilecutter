# coding: UTF-8

import codecs

# Codec for converting windows-style newlines to unix-style ones
class Codec(codecs.Codec):
    def encode(self, input, errors="strict"):
        return input.replace("\r\n", "\n"), len(input)

    def decode(self, input, errors="strict"):
        return input.replace("\r\n", "\n"), len(input)

class StreamWriter(Codec, codecs.StreamWriter): pass
class StreamReader(Codec, codecs.StreamWriter): pass

def getregentry(dec=None):
    if dec == "u_newlines":
        return codecs.CodecInfo(Codec().encode, Codec().decode, StreamReader, StreamWriter, name="u_newlines")

codecs.register(getregentry)


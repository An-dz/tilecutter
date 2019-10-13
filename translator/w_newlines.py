import codecs


# Codec for converting unix-style newlines to windows-style ones
class Codec(codecs.Codec):
    def encode(self, text, errors="strict"):
        return text.replace("\n", "\r\n"), len(text)

    def decode(self, text, errors="strict"):
        return text.replace("\n", "\r\n"), len(text)


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamWriter):
    pass


def getregentry(dec=None):
    if dec == "w_newlines":
        return codecs.CodecInfo(Codec().encode, Codec().decode, StreamReader, StreamWriter, name="w_newlines")


codecs.register(getregentry)

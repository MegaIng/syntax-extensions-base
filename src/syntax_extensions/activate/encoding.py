import sys
from codecs import Codec, BufferedIncrementalDecoder, CodecInfo
from io import BytesIO
from typing import Tuple
from encodings import utf_8
from syntax_extensions.base.apply import apply

def decode(inp: bytes, errors='strict') -> Tuple[str, int]:
    try:
        s, con = utf_8.decode(inp, errors)
        s = apply(s) + "\n"
        return s, con
    except Exception as e:
        sys.excepthook(*sys.exc_info())
        raise

class SyntaxExtensionIncrementalDecoder(BufferedIncrementalDecoder):
    def _buffer_decode(self, inp, errors, final):
        if final:
            return decode(inp, errors)
        else:
            return '', 0

class SyntaxExtensionStreamReader(utf_8.StreamReader, object):
    """decode is deferred to support better error messages"""
    _stream = None
    _decoded = False

    @property
    def stream(self):
        if not self._decoded:
            text, _ = decode(self._stream.read())
            self._stream = BytesIO(text.encode('UTF-8'))
            self._decoded = True
        return self._stream

    @stream.setter
    def stream(self, stream):
        self._stream = stream
        self._decoded = False

codec_info = CodecInfo(
    encode=utf_8.encode,
    decode=decode,
    streamreader=SyntaxExtensionStreamReader,
    streamwriter=utf_8.StreamWriter,
    incrementalencoder=utf_8.IncrementalEncoder,
    incrementaldecoder=SyntaxExtensionIncrementalDecoder,
    name='syntax-extensions'
)
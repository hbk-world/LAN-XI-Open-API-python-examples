# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class OpenapiHeader(KaitaiStruct):

    class EMessageType(Enum):
        e_sequence_data = 1
        e_data_quality = 2
        state = 3
        status = 4
        trigger = 5
        node = 6
        sync = 7
        debug = 9
        package = 10
        aux_sequence_data = 11
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = self._io.ensure_fixed_contents(b"\x42\x4B")
        self.header_length = self._io.read_u2le()
        self.message_type = KaitaiStream.resolve_enum(self._root.EMessageType, self._io.read_u2le())
        self.reserved1 = self._io.read_u2le()
        self.reserved2 = self._io.read_u4le()
        self.time = self._io.read_u4le()
        self.time2 = self._io.read_u8le()
        self.content_length = self._io.read_u4le()



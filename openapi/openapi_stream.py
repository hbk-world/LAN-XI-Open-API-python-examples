# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class OpenapiStream(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = self._root.Header(self._io, self, self._root)
        _on = self.header.message_type
        if _on == self._root.Header.EMessageType.e_interpretation:
            self._raw_content = self._io.read_bytes(self.header.content_length)
            _io__raw_content = KaitaiStream(BytesIO(self._raw_content))
            self.content = self._root.InterpretationList(_io__raw_content, self, self._root)
        elif _on == self._root.Header.EMessageType.e_aux_sequence_data:
            self._raw_content = self._io.read_bytes(self.header.content_length)
            _io__raw_content = KaitaiStream(BytesIO(self._raw_content))
            self.content = self._root.AuxSequenceData(_io__raw_content, self, self._root)
        elif _on == self._root.Header.EMessageType.e_data_quality:
            self._raw_content = self._io.read_bytes(self.header.content_length)
            _io__raw_content = KaitaiStream(BytesIO(self._raw_content))
            self.content = self._root.DataQuality(_io__raw_content, self, self._root)
        elif _on == self._root.Header.EMessageType.e_signal_data:
            self._raw_content = self._io.read_bytes(self.header.content_length)
            _io__raw_content = KaitaiStream(BytesIO(self._raw_content))
            self.content = self._root.SignalData(_io__raw_content, self, self._root)
        else:
            self.content = self._io.read_bytes(self.header.content_length)

    class AuxSignal(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.signal_id = self._io.read_u2le()
            self.number_of_values = self._io.read_u2le()
            self.data = [None] * (self.number_of_values)
            for i in range(self.number_of_values):
                self.data[i] = self._root.AuxData(self._io, self, self._root)



    class TimeStamp(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.time_family = self._root.TimeFamily(self._io, self, self._root)
            self.stamp = self._io.read_u8le()


    class DataQuality(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.number_of_signals = self._io.read_u2le()
            self.qualities = [None] * (self.number_of_signals)
            for i in range(self.number_of_signals):
                self.qualities[i] = self._root.QualityBlock(self._io, self, self._root)



    class AuxSequenceData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.number_of_signals = self._io.read_u2le()
            self.reserved = self._io.read_u2le()
            self.signals = [None] * (self.number_of_signals)
            for i in range(self.number_of_signals):
                self.signals[i] = self._root.AuxSignal(self._io, self, self._root)



    class Interpretation(KaitaiStruct):

        class EDescriptorType(Enum):
            data_type = 1
            scale_factor = 2
            offset = 3
            period_time = 4
            unit = 5
            vector_length = 6
            channel_type = 7

        class EChannelType(Enum):
            none = 0
            analog_input_channel = 1
            aux_input_channel = 2
            can_bus = 3
            analog_output_channel = 20
            aux_output_channel = 21

        class EContentDataType(Enum):
            unknown = 0
            byte = 1
            int16 = 2
            int24 = 3
            int32 = 4
            int64 = 5
            float32 = 6
            float64 = 7
            complex32 = 8
            complex64 = 9
            string = 10
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.signal_id = self._io.read_u2le()
            self.descriptor_type = KaitaiStream.resolve_enum(self._root.Interpretation.EDescriptorType, self._io.read_u2le())
            self.reserved = self._io.read_u2le()
            self.value_length = self._io.read_u2le()
            _on = self.descriptor_type
            if _on == self._root.Interpretation.EDescriptorType.data_type:
                self.value = self._io.read_u4le()
            elif _on == self._root.Interpretation.EDescriptorType.scale_factor:
                self.value = self._io.read_f8le()
            elif _on == self._root.Interpretation.EDescriptorType.unit:
                self.value = self._root.String(self._io, self, self._root)
            elif _on == self._root.Interpretation.EDescriptorType.vector_length:
                self.value = self._io.read_u4le()
            elif _on == self._root.Interpretation.EDescriptorType.period_time:
                self.value = self._root.TimeStamp(self._io, self, self._root)
            elif _on == self._root.Interpretation.EDescriptorType.offset:
                self.value = self._io.read_f8le()
            elif _on == self._root.Interpretation.EDescriptorType.channel_type:
                self.value = self._io.read_u4le()


    class String(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.count = self._io.read_u2le()
            self.data = (self._io.read_bytes((self.count + (self.count % 2)))).decode(u"UTF8")


    class TimeFamily(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.k = self._io.read_u1()
            self.l = self._io.read_u1()
            self.m = self._io.read_u1()
            self.n = self._io.read_u1()


    class QualityBlock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.signal_id = self._io.read_u2le()
            self.validity = self._io.read_u2le()
            self.reserved = self._io.read_u2le()


    class SignalData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.number_of_signals = self._io.read_s2le()
            self.reserved = self._io.read_u2le()
            self.signals = [None] * (self.number_of_signals)
            for i in range(self.number_of_signals):
                self.signals[i] = self._root.SignalBlock(self._io, self, self._root)



    class AuxData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.relative_time = self._io.read_u4le()
            self.values = self._root.CanMessage(self._io, self, self._root)


    class Header(KaitaiStruct):

        class EMessageType(Enum):
            unknown = 0
            e_signal_data = 1
            e_data_quality = 2
            e_interpretation = 8
            e_aux_sequence_data = 11
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.ensure_fixed_contents(b"\x42\x4B")
            self.header_length = self._io.read_u2le()
            self.message_type = KaitaiStream.resolve_enum(self._root.Header.EMessageType, self._io.read_u2le())
            self.reserved1 = self._io.read_u2le()
            self.reserved2 = self._io.read_u4le()
            self.time_family = self._root.TimeFamily(self._io, self, self._root)
            self.time_count = self._io.read_u8le()
            self.content_length = self._io.read_u4le()


    class CanMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.status = self._io.read_u1()
            self.can_message_info = self._io.read_u1()
            self.can_data_size = self._io.read_u1()
            self.reserved = self._io.read_u1()
            self.can_message_id = self._io.read_u4le()
            self.can_data = self._io.read_u8le()


    class SignalBlock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.signal_id = self._io.read_s2le()
            self.number_of_values = self._io.read_s2le()
            self.values = [None] * (self.number_of_values)
            for i in range(self.number_of_values):
                self.values[i] = self._root.Value(self._io, self, self._root)



    class InterpretationList(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.interpretations = []
            i = 0
            while not self._io.is_eof():
                self.interpretations.append(self._root.Interpretation(self._io, self, self._root))
                i += 1



    class Value(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.value1 = self._io.read_u1()
            self.value2 = self._io.read_u1()
            self.value3 = self._io.read_s1()

        @property
        def calc_value(self):
            if hasattr(self, '_m_calc_value'):
                return self._m_calc_value if hasattr(self, '_m_calc_value') else None

            self._m_calc_value = ((self.value1 + (self.value2 << 8)) + (self.value3 << 16))
            return self._m_calc_value if hasattr(self, '_m_calc_value') else None




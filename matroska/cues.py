from ebml.base import EBMLMasterElement, EBMLInteger, EBMLList, EBMLProperty, EBMLData
import ebml.exceptions
from ebml.util import fromVint
import regex

intmatch = b"(?:" + b"|".join(rf"\x{128+n:02x}[\x00-\xff]{{{n}}}".encode("utf8") for n in range(1, 9)) + b")"
vintmatch = b"(?:" + b"|".join((rf"[\x{2**(8 - n):02x}-\x{2**(9 - n) - 1:02x}][\x00-\xff]{{{n-1}}}").encode("utf8") for n in range(1, 9)) + b")"
intparse = rb"[\x81-\x88]([\x00-\xff]+)"

class CueMasterElement(EBMLMasterElement):
    @classmethod
    def fromBytes(cls, data, parent=None):
        vint, data = regex.findall(cls.re_parse, data)[0]
        if fromVint(vint) != len(data):
            raise ebml.exceptions.DecodeError("Advertised size does not match actual size.")

        return cls._fromBytes(data, parent)

    @classmethod
    def _fromBytes(cls, data, parent=None):
        self = cls.__new__(cls)
        self._parent = parent

        for childData, garbage in regex.findall(self.re_itemparse, data):
            if garbage:
                print((childData, garbage), self.re_itemparse, "*",  data)
                raise ebml.exceptions.DecodeError(f"Garbage found attempting to decode {cls} object.")

            if len(childData) == 0:
                break

            ebmlID = regex.match(vintmatch, childData).group()
            prop = self.__ebmlpropertiesbyid__[ebmlID]
            childcls = self._childTypes[ebmlID]
            child = childcls.fromBytes(childData, parent=self)

            if issubclass(prop.cls, EBMLList):
                if not hasattr(self, f"_{prop.attrname}"):
                    prop.__set__(self, [child])

                else:
                    prop.__get__(self).append(child)

            else:
                prop.__set__(self, child)

        return self

    def __init_subclass__(cls):
        _children_matches = []

        for prop in cls.__ebmlchildren__:
            if issubclass(prop.cls, EBMLList):
                _children_matches.append(prop.cls.itemclass.re_match)

            else:
                _children_matches.append(prop.cls.re_match)

        _children_matches = b"(?:" + b"|".join(_children_matches) + b")"
        cls.re_match = regex.escape(cls.ebmlID) + vintmatch +  _children_matches + b"*"
        cls.re_parse = b"^" + regex.escape(cls.ebmlID) + b"(" + vintmatch + b")(" + _children_matches + b"*)$"
        cls.re_itemparse = b"(" + _children_matches + b")|([\\x00-\\xff]+)$"

class CueInteger(EBMLInteger):
    @classmethod
    def fromBytes(cls, data, parent=None):
        data = regex.findall(cls.re_parse, data)[0]
        return cls._fromBytes(data, parent)

    @classmethod
    def _fromBytes(cls, data, parent=None):
        self = cls.__new__(cls)
        self._parent = parent
        self._data = int.from_bytes(data, "big")
        return self

    def __init_subclass__(cls):
        cls.re_match = regex.escape(cls.ebmlID) + intmatch
        cls.re_parse = b"^" + regex.escape(cls.ebmlID) + intparse + b"$"

class CueRefTime(CueInteger):
    ebmlID = b"\x96"

class CueReference(CueMasterElement):
    ebmlID = b"\xdb"
    __ebmlchildren__ = (
            EBMLProperty("cueRefTime", CueRefTime),
        )

class CueTrack(CueInteger):
    ebmlID = b"\xf7"

class CueClusterPosition(CueInteger):
    ebmlID = b"\xf1"

class CueRelativePosition(CueInteger):
    ebmlID = b"\xf0"

class CueDuration(CueInteger):
    ebmlID = b"\xb2"

class CueBlockNumber(CueInteger):
    ebmlID = b"\x53\x78"

class CueCodecState(CueInteger):
    ebmlID = b"\xea"

class CueReferences(EBMLList):
    itemclass = CueReference

class CueTrackPositions(CueMasterElement):
    ebmlID = b"\xb7"
    __ebmlchildren__ = (
            EBMLProperty("cueTrack", CueTrack),
            EBMLProperty("cueClusterPosition", CueClusterPosition),
            EBMLProperty("cueRelativePosition", CueRelativePosition, True),
            EBMLProperty("cueDuration", CueDuration, True),
            EBMLProperty("cueBlockNumber", CueBlockNumber, True),
            EBMLProperty("cueCodecState", CueCodecState, True),
            EBMLProperty("cueReferences", CueReferences, optional=True),
        )

class CueTime(CueInteger):
    ebmlID = b"\xb3"

class CueTrackPositionsList(EBMLList):
    itemclass = CueTrackPositions


class CuePoint(CueMasterElement):
    ebmlID = b"\xbb"

    __ebmlchildren__ = (
            EBMLProperty("cueTime", CueTime),
            EBMLProperty("cueTrackPositionsList", CueTrackPositionsList),
        )

    __ebmladdproperties__ = (
            EBMLProperty("data", bytes, optional=True),
        )

class CuePoints(EBMLList):
    itemclass = CuePoint


class Cues(CueMasterElement):
    ebmlID = b"\x1c\x53\xbb\x6b"
    __ebmlchildren__ = (EBMLProperty("cuePoints", CuePoints),)

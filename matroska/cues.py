from ebml.base import EBMLMasterElement, EBMLInteger, EBMLList, EBMLProperty, EBMLData
#from ebml.util import EBMLList, EBMLProperty, EBMLProperty

class CueRefTime(EBMLInteger):
    ebmlID = b"\x96"

class CueReference(EBMLMasterElement):
    ebmlID = b"\xdb"
    __ebmlchildren__ = (
            EBMLProperty("cueRefTime", CueRefTime),
        )

class CueTrack(EBMLInteger):
    ebmlID = b"\xf7"

class CueClusterPosition(EBMLInteger):
    ebmlID = b"\xf1"

class CueRelativePosition(EBMLInteger):
    ebmlID = b"\xf0"

class CueDuration(EBMLInteger):
    ebmlID = b"\xb2"

class CueBlockNumber(EBMLInteger):
    ebmlID = b"\x53\x78"

class CueCodecState(EBMLInteger):
    ebmlID = b"\xea"

class CueReferences(EBMLList):
    itemclass = CueReference

class CueTrackPositions(EBMLMasterElement):
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

#class CueTrackPositions(EBMLData):
    #ebmlID = b"\xb7"

class CueTime(EBMLInteger):
    ebmlID = b"\xb3"

class CueTrackPositionsList(EBMLList):
    #itemclass = (CueTrackPositionsPointer, CueTrackPositions)
    itemclass = CueTrackPositions


class CuePoint(EBMLMasterElement):
    ebmlID = b"\xbb"

    __ebmlchildren__ = (
            EBMLProperty("cueTime", CueTime),
            EBMLProperty("cueTrackPositionsList", CueTrackPositionsList),
        )

    __ebmlproperties__ = (
            EBMLProperty("data", bytes, optional=True),
        )

    @classmethod
    def _fromBytes(cls, data, ebmlID=None, parent=None):
        self = cls.__new__(cls)
        self._data = data
        self._parent = parent

        if cls.ebmlID is None:
            self._ebmlID = ebmlID

        return self

    def _decodeData(self):
        rostatus = self.readonly
        self._readonly = False
        super(CuePoint, self)._decodeData(self.data)
        self._data = None
        self.readonly = rostatus

    @property
    def cueTime(self):
        prop = self.__ebmlpropertiesbyid__[CueTime.ebmlID]

        if not hasattr(self, f"_{prop.attrname}"):
            self._decodeData()

        return prop.__get__(self)

    @cueTime.setter
    def cueTime(self, value):
        prop = self.__ebmlpropertiesbyid__[CueTime.ebmlID]
        return prop.__set__(self, value)

    @property
    def cueTrackPositionsList(self):
        prop = self.__ebmlpropertiesbyid__[CueTrackPositions.ebmlID]

        if not hasattr(self, f"_{prop.attrname}"):
            self._decodeData()

        return prop.__get__(self)

    @cueTrackPositionsList.setter
    def cueTrackPositionsList(self, value):
        prop = self.__ebmlpropertiesbyid__[CueTrackPositions.ebmlID]
        return prop.__set__(self, value)

    def __repr__(self):
        if self._data:
            self._decodeData()

        return super(CuePoint, self).__repr__()

#class CuePoint(EBMLData):
    #ebmlID = b"\xbb"


class CuePoints(EBMLList):
    #itemclass = (CuePointPointer, CuePoint)
    itemclass = CuePoint


class Cues(EBMLMasterElement):
    ebmlID = b"\x1c\x53\xbb\x6b"
    __ebmlchildren__ = (EBMLProperty("cuePoints", CuePoints),)

#class Cues(EBMLData):
    #ebmlID = b"\x1c\x53\xbb\x6b"


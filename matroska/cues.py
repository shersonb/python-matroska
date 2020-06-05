from ebml.base import EBMLMasterElement, EBMLInteger, EBMLList, EBMLProperty, EBMLData

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

class CueTime(EBMLInteger):
    ebmlID = b"\xb3"

class CueTrackPositionsList(EBMLList):
    itemclass = CueTrackPositions


class CuePoint(EBMLMasterElement):
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


class Cues(EBMLMasterElement):
    ebmlID = b"\x1c\x53\xbb\x6b"
    __ebmlchildren__ = (EBMLProperty("cuePoints", CuePoints),)

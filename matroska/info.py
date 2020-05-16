from ebml.base import EBMLInteger, EBMLData, EBMLString, EBMLMasterElement, EBMLFloat, EBMLDateTime, EBMLList, EBMLProperty
#from ebml.util import EBMLList, EBMLProperty, EBMLProperty

class TimestampScale(EBMLInteger):
    ebmlID = b"\x2a\xd7\xb1"

class MuxingApp(EBMLString):
    ebmlID = b"\x4d\x80"

class WritingApp(EBMLString):
    ebmlID = b"\x57\x41"

class SegmentUID(EBMLData):
    ebmlID = b"\x73\xa4"

class SegmentFilename(EBMLString):
    ebmlID = b"\x73\x84"

class PrevUID(EBMLData):
    ebmlID = b"\x3c\xb9\x23"

class PrevFilename(EBMLString):
    ebmlID = b"\x3c\x83\xab"

class NextUID(EBMLData):
    ebmlID = b"\x3e\xb9\x23"

class NextFilename(EBMLString):
    ebmlID = b"\x3e\x83\xbb"

class SegmentFamily(EBMLData):
    ebmlID = b"\x44\x44"

class SegmentFamilies(EBMLList):
    itemclass = SegmentFamily
    attrname = "data"

class ChapterTranslateEditionUID(EBMLInteger):
    ebmlID = b"\x69\xfc"

class ChapterTranslateCodec(EBMLInteger):
    ebmlID = b"\x69\xbf"

class ChapterTranslateID(EBMLData):
    ebmlID = b"\x69\xa5"

class ChapterTranslate(EBMLMasterElement):
    ebmlID = b"\x69\x24"
    __ebmlchildren__ = (
            EBMLProperty("chapterTranslateEditionUID", ChapterTranslateEditionUID, True),
            EBMLProperty("chapterTranslateCodec", ChapterTranslateCodec),
            EBMLProperty("chapterTranslateID", ChapterTranslateID)
        )

class ChapterTranslates(EBMLList):
    itemclass = ChapterTranslate

class Duration(EBMLFloat):
    ebmlID = b"\x44\x89"

class DateUTC(EBMLDateTime):
    ebmlID = b"\x44\x61"

class Title(EBMLString):
    ebmlID = b"\x7b\xa9"

class Info(EBMLMasterElement):
    ebmlID = b"\x15\x49\xa9\x66"
    __ebmlchildren__ = (
            EBMLProperty("timestampScale", TimestampScale),
            EBMLProperty("muxingApp", MuxingApp),
            EBMLProperty("writingApp", WritingApp),
            EBMLProperty("segmentUID", SegmentUID, True),
            EBMLProperty("segmentFilename", SegmentFilename, True),
            EBMLProperty("prevUID", PrevUID, True),
            EBMLProperty("prevFilename", PrevFilename, True),
            EBMLProperty("nextUID", NextUID, True),
            EBMLProperty("nextFilename", NextFilename, True),
            EBMLProperty("segmentFamilies", SegmentFamilies, True),
            EBMLProperty("chapterTranslates", ChapterTranslates, True),
            EBMLProperty("duration", Duration, True),
            EBMLProperty("dateUTC", DateUTC, True),
            EBMLProperty("title", Title, True)
        )


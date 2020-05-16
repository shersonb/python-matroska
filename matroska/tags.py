from ebml.base import EBMLInteger, EBMLString, EBMLMasterElement, EBMLData, EBMLList, EBMLProperty
#from ebml.util import EBMLList, EBMLProperty, EBMLProperty

class TargetTypeValue(EBMLInteger):
    ebmlID = b"\x68\xca"

class TargetType(EBMLString):
    ebmlID = b"\x63\xca"

class TagTrackUID(EBMLInteger):
    ebmlID = b"\x63\xc5"

class TagEditionUID(EBMLInteger):
    ebmlID = b"\x63\xc9"

class TagChapterUID(EBMLInteger):
    ebmlID = b"\x63\xc4"

class TagAttachmentUID(EBMLInteger):
    ebmlID = b"\x63\xc6"


class TagTrackUIDs(EBMLList):
    itemclass = TagTrackUID
    attrname =  "value"

class TagEditionUIDs(EBMLList):
    itemclass = TagEditionUID
    attrname = "value"

class TagChapterUIDs(EBMLList):
    itemclass = TagChapterUID
    attrname = "value"

class TagAttachmentUIDs(EBMLList):
    itemclass = TagAttachmentUID
    attrname = "value"


class Targets(EBMLMasterElement):
    ebmlID = b"\x63\xc0"
    __ebmlchildren__ = (
            EBMLProperty("targetTypeValue", TargetTypeValue, True),
            EBMLProperty("targetType", TargetType, True),
            EBMLProperty("tagTrackUIDs", TagTrackUIDs, optional=True),
            EBMLProperty("tagEditionUIDs", TagEditionUIDs, optional=True),
            EBMLProperty("tagChapterUIDs", TagChapterUIDs, optional=True),
            EBMLProperty("tagAttachmentUIDs", TagAttachmentUIDs, optional=True),
        )

class TagName(EBMLString):
    ebmlID = b"\x45\xa3"

class TagLanguage(EBMLString):
    ebmlID = b"\x44\x7a"
    encoding="ascii"

class TagLanguageIETF(EBMLString):
    ebmlID = b"\x44\x7b"
    encoding="ascii"

class TagDefault(EBMLInteger):
    ebmlID = b"\x44\x84"

class TagString(EBMLString):
    ebmlID = b"\x44\x87"

class TagBinary(EBMLData):
    ebmlID = b"\x44\x85"


class SimpleTag(EBMLMasterElement):
    ebmlID = b"\x67\xc8"
    __ebmlchildren__ = (
            EBMLProperty("tagName", TagName),
            EBMLProperty("tagLanguage", TagLanguage, True),
            EBMLProperty("tagLanguageIETF", TagLanguageIETF, True),
            EBMLProperty("tagDefault", TagDefault, True),
            EBMLProperty("tagString", TagString, True),
            EBMLProperty("tagBinary", TagBinary, True),
        )

class SimpleTags(EBMLList):
    itemclass = SimpleTag


class Tag(EBMLMasterElement):
    ebmlID = b"\x73\x73"
    __ebmlchildren__ = (
            EBMLProperty("targets", Targets),
            EBMLProperty("simpleTags", SimpleTags),
        )

class TagList(EBMLList):
    itemclass = Tag


class Tags(EBMLMasterElement):
    ebmlID = b"\x12\x54\xc3\x67"
    __ebmlchildren__ = (EBMLProperty("tagList", TagList),)

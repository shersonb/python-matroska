from ebml.base import EBMLInteger, EBMLData, EBMLString, EBMLMasterElement, EBMLList, EBMLProperty
#from ebml.util import EBMLList, EBMLProperty, EBMLProperty

class ChapterTrackNumber(EBMLInteger):
    ebmlID = b"\x89"

class ChapterTrackNumbers(EBMLList):
    itemclass = ChapterTrackNumber

class ChapterTrack(EBMLMasterElement):
    ebmlID = b"\x8f"
    __ebmlchildren__ = (
            EBMLProperty("chapterTrackNumbers", ChapterTrackNumbers),
        )

class ChapString(EBMLString):
    ebmlID = b"\x85"

class ChapLanguage(EBMLString):
    ebmlID = b"\x43\x7c"

class ChapLanguages(EBMLList):
    itemclass = ChapLanguage
    attrname = "value"

class ChapLanguageIETF(EBMLString):
    ebmlID = b"\x43\x7d"

class ChapCountry(EBMLString):
    ebmlID = b"\x43\x7e"

class ChapCountries(EBMLList):
    itemclass = ChapCountry
    attrname = "value"

class ChapterDisplay(EBMLMasterElement):
    ebmlID = b"\x80"
    __ebmlchildren__ = (
            EBMLProperty("chapString", ChapString),
            EBMLProperty("chapLanguages", ChapLanguages),
            EBMLProperty("chapLanguageIETF", ChapLanguageIETF, True),
            EBMLProperty("chapCountries", ChapCountries, True)
        )

class ChapterDisplays(EBMLList):
    itemclass = ChapterDisplay

class ChapProcessCodecID(EBMLInteger):
    ebmlID = b"\x69\x55"

class ChapProcessPrivate(EBMLData):
    ebmlID = b"\x45\x0d"

class ChapProcessTime(EBMLInteger):
    ebmlID = b"\x69\x22"

class ChapProcessData(EBMLData):
    ebmlID = b"\x69\x33"

class ChapProcessCommand(EBMLMasterElement):
    ebmlID = b"\x45\x0d"
    __ebmlchildren__ = (
            EBMLProperty("chapProcessTime", ChapProcessTime),
            EBMLProperty("chapProcessData", ChapProcessData),
        )

class ChapProcessCommands(EBMLList):
    itemclass = ChapProcessCommand


class ChapterProcess(EBMLMasterElement):
    ebmlID = b"\x69\x44"
    __ebmlchildren__ = (
            EBMLProperty("chapProcessCodecID", ChapProcessCodecID),
            EBMLProperty("chapProcessPrivate", ChapProcessPrivate),
            EBMLProperty("chapProcessCommands", ChapProcessCommands, optional=True)
        )

class ChapterUID(EBMLInteger):
    ebmlID = b"\x73\xc4"

class ChapterStringUID(EBMLString):
    ebmlID = b"\x56\x54"

class ChapterTimeStart(EBMLInteger):
    ebmlID = b"\x91"

class ChapterTimeEnd(EBMLInteger):
    ebmlID = b"\x92"

class ChapterFlagHidden(EBMLInteger):
    ebmlID = b"\x98"

class ChapterFlagEnabled(EBMLInteger):
    ebmlID = b"\x45\x98"

class ChapterSegmentUID(EBMLData):
    ebmlID = b"\x6e\x67"

ChapterSegmentEditionUID = EBMLInteger.makesubclass("ChapterSegmentUID", prefix=b"\x6e\xbc")
class ChapterPhysicalEquiv(EBMLInteger):
    ebmlID = b"\x63\xc3"


class ChapterTrackNumber(EBMLInteger):
    ebmlID = b"\x89"

class ChapterTrackNumbers(EBMLList):
    itemclass = ChapterTrackNumber
    #attrname = "value"


class ChapterTrack(EBMLMasterElement):
    ebmlID = b"\x8f"
    __ebmlchildren__ = (
            EBMLProperty("chapterTrackNumbers", ChapterTrackNumbers),
        )

class ChapterProcesses(EBMLList):
    itemclass = ChapterProcess


class ChapterAtom(EBMLMasterElement):
    ebmlID = b"\xb6"
    __ebmlchildren__ = (
            EBMLProperty("chapterUID", ChapterUID),
            EBMLProperty("chapterStringUID", ChapterStringUID, True),
            EBMLProperty("chapterTimeStart", ChapterTimeStart),
            EBMLProperty("chapterTimeEnd", ChapterTimeEnd),
            EBMLProperty("chapterFlagHidden", ChapterFlagHidden),
            EBMLProperty("chapterFlagEnabled", ChapterFlagEnabled),
            EBMLProperty("chapterSegmentUID", ChapterSegmentUID, True),
            EBMLProperty("chapterSegmentEditionUID", ChapterSegmentEditionUID, True),
            EBMLProperty("chapterPhysicalEquiv", ChapterPhysicalEquiv, True),
            EBMLProperty("chapterTrack", ChapterTrack, True),
            EBMLProperty("chapterDisplays", ChapterDisplays, True),
            EBMLProperty("chapterProcesses", ChapterProcesses, True)
        )

class ChapterAtoms(EBMLList):
    itemclass = ChapterAtom


class EditionUID(EBMLInteger):
    ebmlID = b"\x45\xbc"

class EditionFlagHidden(EBMLInteger):
    ebmlID = b"\x45\xbd"

class EditionFlagDefault(EBMLInteger):
    ebmlID = b"\x45\xdb"

class EditionFlagOrdered(EBMLInteger):
    ebmlID = b"\x45\xdd"


class EditionEntry(EBMLMasterElement):
    ebmlID = b"\x45\xb9"
    __ebmlchildren__ = (
            EBMLProperty("editionUID", EditionUID),
            EBMLProperty("editionFlagHidden", EditionFlagHidden),
            EBMLProperty("editionFlagDefault", EditionFlagDefault),
            EBMLProperty("editionFlagOrdered", EditionFlagOrdered, True),
            EBMLProperty("chapterAtoms", ChapterAtoms)
        )
    @property
    def append(self):
        return self.chapterAtoms.append

    @property
    def insert(self):
        return self.chapterAtoms.insert

    @property
    def remove(self):
        return self.chapterAtoms.remove

    @property
    def extend(self):
        return self.chapterAtoms.extend

    @property
    def __iter__(self):
        return self.chapterAtoms.__iter__

    @property
    def __getitem__(self):
        return self.chapterAtoms.__getitem__

class EditionEntries(EBMLList):
    itemclass = EditionEntry


class Chapters(EBMLMasterElement):
    ebmlID = b"\x10\x43\xa7\x70"
    __ebmlchildren__ = (EBMLProperty("editionEntries", EditionEntries),)

    @property
    def append(self):
        return self.editionEntries.append

    @property
    def insert(self):
        return self.editionEntries.insert

    @property
    def remove(self):
        return self.editionEntries.remove

    @property
    def extend(self):
        return self.editionEntries.extend

    @property
    def __iter__(self):
        return self.editionEntries.__iter__

    @property
    def __getitem__(self):
        return self.editionEntries.__getitem__

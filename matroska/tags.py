from ebml.base import EBMLInteger, EBMLString, EBMLMasterElement, EBMLData, EBMLList, EBMLProperty
import matroska.chapters

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

SimpleTag.__ebmlchildren__ += (EBMLProperty("simpleTags", SimpleTags, optional=True),)
SimpleTag._prepare()
SimpleTag._generate__init__()

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

    @property
    def append(self):
        return self.tagList.append

    @property
    def insert(self):
        return self.tagList.insert

    @property
    def remove(self):
        return self.tagList.remove

    @property
    def extend(self):
        return self.tagList.extend

    @property
    def __iter__(self):
        return self.tagList.__iter__

    @property
    def __getitem__(self):
        return self.tagList.__getitem__

    def addMovieTag(self, title, director=None, dateReleased=None, comment=None):
        targets = Targets(targetTypeValue=50, targetType="MOVIE")
        simpleTags = [SimpleTag(tagName="TITLE", tagString=title)]

        if director is not None:
            simpleTags.append(SimpleTag(tagname="DIRECTOR", tagString=director))

        if dateReleased is not None:
            simpleTags.append(SimpleTag(tagname="DATE_RELEASED", tagString=dateReleased))

        if comment is not None:
            simpleTags.append(SimpleTag(tagname="COMMENT", tagString=comment))

        tag = Tag(targets, simpleTags)
        self.append(tag)
        return tag

    def addCollectionTag(self, title):
        targets = Targets(targetTypeValue=70, targetType="COLLECTION")
        simpleTags = [SimpleTag(tagName="TITLE", tagString=title)]

        tag = Tag(targets, simpleTags)
        self.append(tag)
        return tag

    def addSeasonTag(self, seasonNumber, dateReleased=None, numberOfEpisodes=None):
        targets = Targets(targetTypeValue=60, targetType="SEASON")
        simpleTags = [SimpleTag(tagName="PART_NUMBER", tagString=seasonNumber)]

        if dateReleased:
            simpleTags.append(SimpleTag(tagName="DATE_RELEASED", tagString=dateReleased))

        if numberOfEpisodes:
            simpleTags.append(SimpleTag(tagName="TOTAL_PARTS", tagString=numberOfEpisodes))

        tag = Tag(targets, simpleTags)
        self.append(tag)
        return tag

    def addEpisodeTag(self, title, part=None, chapters=()):
        targets = Targets(targetTypeValue=50, targetType="EPISODE")
        simpleTags = [SimpleTag(tagName="TITLE", tagString=title)]

        if part is not None:
            simpleTags.append(SimpleTag(tagName="PART_NUMBER", tagString=part))

        if chapters:
            targets.tagChapterUIDs = []

            for chapter in chapters:
                if isinstance(chapter, matroska.chapters.ChapterAtom):
                    targets.tagChapterUIDs.append(chapter.chapterUID)

                else:
                    targets.tagChapterUIDs.append(chapter)

        tag = Tag(targets, simpleTags)
        self.append(tag)
        return tag

    def addChapterTag(self, chapterUID, title):
        targets = Targets(chapterUID=chapterUID, targetTypeValue=30, targetType="CHAPTER")
        simpleTags = [SimpleTag(tagName="TITLE", tagString=title)]

        tag = Tag(targets, simpleTags)
        self.append(tag)
        return tag


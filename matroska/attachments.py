from ebml.base import EBMLInteger, EBMLData, EBMLString, EBMLMasterElement, EBMLFloat, EBMLList, EBMLProperty
#from ebml.util import EBMLList, EBMLProperty, EBMLProperty

class FileName(EBMLString):
    ebmlID = b"\x46\x6e"

class FileDescription(EBMLString):
    ebmlID = b"\x46\x7e"

class FileMimeType(EBMLString):
    ebmlID = b"\x46\x60"

class FileData(EBMLData):
    ebmlID = b"\x46\x5c"

class FileUID(EBMLInteger):
    ebmlID = b"\x46\xae"

class AttachedFile(EBMLMasterElement):
    __ebmlchildren__ = (
            EBMLProperty("fileName", FileName),
            EBMLProperty("mimeType", FileMimeType),
            EBMLProperty("fileData", FileData),
            EBMLProperty("UID", FileUID),
            EBMLProperty("description", FileDescription, True),
        )
    ebmlID = b"\x61\xa7"

class AttachedFiles(EBMLList):
    itemclass = AttachedFile

class Attachments(EBMLMasterElement):
    __ebmlchildren__ = (
            EBMLProperty("attachedFiles", AttachedFiles),
        )
    ebmlID = b"\x19\x41\xa4\x69"

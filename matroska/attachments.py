from ebml.base import EBMLInteger, EBMLData, EBMLString, EBMLMasterElement, EBMLFloat, EBMLList, EBMLProperty
import ebml.util
import io
import mimetypes
import os
import random
from itertools import count

class FilePointer(object):
    def __init__(self, file, lock, offset, size):
        if not isinstance(file, io.BufferedReader):
            raise TypeError("File is not of type io.BufferedReader.")

        if not file.seekable():
            raise ValueError("io.BufferedReader not seekable.")

        self.file = file
        self.lock = lock
        self.offset = offset
        self.size = size

    def __iter__(self):
        offset = self.offset
        endoffset = offset + self.size

        while offset < endoffset:
            with self.lock:
                self.file.seek(offset)
                data = self.file.read(min(256*1024, endoffset - offset))
                offset = self.file.tell()

            yield data

class FileName(EBMLString):
    ebmlID = b"\x46\x6e"

class FileDescription(EBMLString):
    ebmlID = b"\x46\x7e"

class FileMimeType(EBMLString):
    ebmlID = b"\x46\x60"

class FileData(EBMLData):
    data = EBMLProperty("data", (bytes, io.BufferedReader, FilePointer))
    ebmlID = b"\x46\x5c"
    __ebmlproperties__ = (data,)

    @data.sethook
    def data(self, value):
        if isinstance(value, io.BufferedReader):
            if not value.seekable():
                raise ValueError("io.BufferedReader not seekable.")

        elif isinstance(value, str):
            value = value.encode("utf8")

        return value

    def __iter__(self):
        if isinstance(self.data, bytes):
            yield self.data

        elif isinstance(self.data, FilePointer):
            for chunk in self.data:
                yield chunk

        elif isinstance(self.data, io.BufferedReader):
            while True:
                chunk = self.data.read(256*1024)
                if len(chunk) == 0:
                    break

                if isinstance(chunk, str):
                    chunk = chunk.encode("utf8")

                yield chunk

    def _size(self):
        if isinstance(self.data, bytes):
            return super()._size(file)

        elif isinstance(self.data, FilePointer):
            return self.data.size

        offset = self.data.tell()
        size = self.data.seek(0, 2)
        self.data.seek(offset)
        return size

    def _toBytes(self):
        return b"".join(self)

    def _toFile(self, file):
        for chunk in self:
            file.write(chunk)

    @classmethod
    def _fromFile(cls, file, size, parent=None):
        if parent is not None:
            self = cls(data=FilePointer(file, parent.body.lock, file.tell(), size), parent=parent)
            file.seek(size, 1)

        else:
            self = super()._fromFile(cls, file, size, parent=parent)

        return self

class FileUID(EBMLInteger):
    ebmlID = b"\x46\xae"

class AttachedFile(EBMLMasterElement):
    __ebmlchildren__ = (
            EBMLProperty("fileName", FileName),
            EBMLProperty("mimeType", FileMimeType),
            EBMLProperty("fileData", FileData),
            EBMLProperty("fileUID", FileUID),
            EBMLProperty("description", FileDescription, True),
        )
    ebmlID = b"\x61\xa7"

    @classmethod
    def fromPath(cls, path, mimeType=None, fileUID=None, description=None, parent=None):
        if mimeType is None:
            mimeType, encoding = mimetypes.MimeTypes().guess_type(path)


        if fileUID is None:
            if parent is not None:
                existingUIDs = parent.byFileUID.keys()

                for fileUID in count(1):
                    if fileUID not in existingUIDs:
                        break

            else:
                fileUID = 1

        fileData = open(path, "rb")
        dir, fileName = os.path.split(path)
        return cls(fileName=fileName, mimeType=mimeType, fileUID=fileUID,
                   fileData=fileData, description=description, parent=None)

    def _toFile(self, file):
        data = b""

        for child in self.iterchildren():
            if isinstance(child, FileData):
                if data:
                    file.write(data)
                    data = b""

                child.toFile(file)

            else:
                data += child.toBytes()

        if data:
            file.write(data)

    @classmethod
    def _fromFile(cls, file, size, parent=None):
        self = cls.__new__(cls)
        self._parent = parent
        dataRead = 0

        while dataRead < size:
            ebmlID = ebml.util.peekVint(file)
            childsize = ebml.util.peekVint(file, len(ebmlID))
            childcls = self._childTypes[ebmlID]
            prop = self.__ebmlpropertiesbyid__[ebmlID]
            child = childcls.fromFile(file, parent=self)
            prop.__set__(self, child)
            dataRead += len(ebmlID) + len(childsize) + ebml.util.fromVint(childsize)

        self.readonly = True
        return self

    def save(self, path, noclobber=False):
        """
        Saves attachment. If 'path' is a directory, then filename from
        'self.fileName' will be appended to 'path'.
        """
        if os.path.isdir(path):
            path = os.path.join(path, self.fileName)

        if os.path.isfile(path) and noclobber:
            raise FileExistsError(f"File already exists: {path}")

        file = open(path, "wb")

        for chunk in self.fileData:
            file.write(chunk)

        file.close()

class AttachedFiles(EBMLList):
    itemclass = AttachedFile

class Attachments(EBMLMasterElement):
    __ebmlchildren__ = (
            EBMLProperty("attachedFiles", AttachedFiles),
        )
    ebmlID = b"\x19\x41\xa4\x69"

    @property
    def append(self):
        return self.attachedFiles.append

    @property
    def insert(self):
        return self.attachedFiles.insert

    @property
    def remove(self):
        return self.attachedFiles.remove

    @property
    def extend(self):
        return self.attachedFiles.extend

    def addFile(self, path, mimeType=None, description=None):
        """
        Adds an attachment from a file, detecting its mimetype automatically if 'mimeType' is not specified.
        """
        attachedFile = AttachedFile.fromPath(path, mimeType=mimeType, description=description, parent=self)
        self.append(attachedFile)
        return attachedFile

    @property
    def __iter__(self):
        return self.attachedFiles.__iter__

    @property
    def __getitem__(self):
        return self.attachedFiles.__getitem__

    @property
    def byFileUID(self):
        return {attachedFile.fileUID: attachedFile for attachedFile in self}

    def clone(self, attachedFile):
        attachedFile = attachedFile.copy(parent=self)
        self.append(attachedFile)
        return attachedFile

    @classmethod
    def _fromFile(cls, file, size, parent=None):
        self = cls([], parent=parent)
        dataRead = 0

        while dataRead < size:
            ebmlID = ebml.util.peekVint(file)
            childsize = ebml.util.peekVint(file, len(ebmlID))
            child = AttachedFile.fromFile(file, parent=self)
            self.attachedFiles.append(child)
            dataRead += len(ebmlID) + len(childsize) + ebml.util.fromVint(childsize)

        return self

    def _toFile(self, file):
        for child in self.iterchildren():
            child.toFile(file)

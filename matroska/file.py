from ebml.head import EBMLHead
from ebml.exceptions import ReadError
from ebml.document import EBMLDocument
import random
from .segment import Segment

class MatroskaFile(EBMLDocument):
    def __init__(self, file, mode="r"):
        super(MatroskaFile, self).__init__(file, mode, bodycls=Segment)

    def _init_read(self):
        head = EBMLHead.fromFile(self._file)

        if head.docType != "matroska":
            raise ReadError("Not a matroska file.")

        self.head = head
        self.body = self._bodycls(self._file)

    def _init_write(self):
        head = EBMLHead(docType="matroska", docTypeReadVersion=2, docTypeVersion=4,
                                  ebmlMaxIDLength=4, ebmlMaxSizeLength=8, ebmlReadVersion=1, ebmlVersion=1)

        self.writeEBMLHead(head)
        self.beginWriteEBMLBody()

    @property
    def writingApp(self):
        return self.body.info.writingApp

    @writingApp.setter
    def writingApp(self, value):
        self.body.info.writingApp = value

    @property
    def title(self):
        return self.body.info.title

    @title.setter
    def title(self, value):
        self.body.info.title = value

    @property
    def mux(self):
        """
        Shortcut to Segment.mux().

        See help(matroska.segment.Segment.mux).
        """
        return self.segment.mux

    @property
    def demux(self):
        """
        Shortcut to Segment.iterPackets().

        See help(matroska.segment.Segment.iterPackets).
        """
        return self.segment.iterPackets

    @property
    def segment(self):
        return self.body

    @property
    def tracks(self):
        return self.segment.tracks

    @property
    def tags(self):
        return self.segment.tags

    @property
    def attachments(self):
        return self.segment.attachments

    @property
    def chapters(self):
        return self.segment.chapters


import ebml
import random
import matroska.segment
import matroska.tracks
import matroska.info

class MatroskaFile(ebml.document.EBMLDocument):
    def __init__(self, file, mode="r"):
        super(MatroskaFile, self).__init__(file, mode, bodycls=matroska.segment.Segment)

    def _init_read(self):
        """
        This should be overridden in subclasses if you are looking to handle specific document types.
        """

        head = ebml.head.EBMLHead.fromFile(self._file)

        if head.docType != "matroska":
            raise ebml.document.ReadError("Not a matroska file.")

        self.head = head
        self.body = self._bodycls(self._file)

    def _init_write(self):
        """
        This should be overridden in subclasses if you are looking to handle specific document types.
        """

        head = ebml.head.EBMLHead(docType="matroska", docTypeReadVersion=2, docTypeVersion=4,
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
        return self.segment.mux

    @property
    def demux(self):
        return self.segment.iterPackets

    @property
    def segment(self):
        return self.body

    @property
    def tracks(self):
        return self.segment.tracks

from ebml.base import EBMLMasterElement, EBMLInteger, EBMLProperty, EBMLList
import matroska.blocks

__all__ = ["Cluster", "Clusters", "ClusterPointer", "Timestamp", "Position", "PrevSize", "SilentTrackNumber", "SilentTrackNumbers", "SilentTracks", "Blocks"]

class Timestamp(EBMLInteger):
    ebmlID = b"\xe7"

class Position(EBMLInteger):
    ebmlID = b"\xa7"

class PrevSize(EBMLInteger):
    ebmlID = b"\xab"

class SilentTrackNumber(EBMLInteger):
    ebmlID = b"\x58\xd7"

class SilentTrackNumbers(EBMLList):
    itemclass = SilentTrackNumber

class SilentTracks(EBMLMasterElement):
    ebmlID = b"\x58\x54"
    __ebmlchildren__ = (
            EBMLProperty("silentTrackNumbers", SilentTrackNumbers),
        )

class Blocks(EBMLList):
    itemclass = (matroska.blocks.SimpleBlock, matroska.blocks.BlockGroup)

class Cluster(EBMLMasterElement):
    ebmlID = b"\x1f\x43\xb6\x75"
    __ebmlchildren__ = (
            EBMLProperty("timestamp", Timestamp),
            EBMLProperty("silentTracks", SilentTracks, optional=True),
            EBMLProperty("position", Position, optional=True),
            EBMLProperty("prevSize", PrevSize, optional=True),
            EBMLProperty("blocks", Blocks)
        )
    __ebmlproperties__ = (
            EBMLProperty("offsetInBody", int, optional=True),
            EBMLProperty("dataSize", int, optional=True)
        )

    @property
    def parent(self):
        try:
            return self._parent
        except AttributeError:
            pass

    @parent.setter
    def parent(self, value):
        self._parent = value
        if hasattr(self, "_blocks") and self.blocks is not None:
            for block in self.blocks:
                block.ancestorChanged()

    def iterPackets(self, offset=0, trackNumber=None):
        for block in self.iterBlocks(offset, trackNumber):
            for packet in block.iterPackets():
                yield packet

    def iterBlocks(self, offset=0, trackNumber=None):
        if hasattr(self, "_blocks"):
            for block in self.blocks:
                if trackNumber is None or block.trackNumber == trackNumber:
                    yield block
        else:
            offset = max(offset, 0)

            while offset < self.dataSize:
                with self.body.lock:
                    self.body.seek(self.offsetInBody + offset)
                    child = self.body.readElement((matroska.blocks.SimpleBlock, matroska.blocks.BlockGroup), parent=self)
                    offset = self.body.tell() - self.offsetInBody

                if child is not None and (trackNumber is None or child.trackNumber == trackNumber):
                    yield child

    @classmethod
    def _fromFile(cls, file, size, ebmlID=None, parent=None):
        if file.seekable() and parent is not None:
            self = cls.__new__(cls)
            self._parent = parent

            with parent.lock:
                self.offsetInBody = parent.tell()
                offset = 0

                for k in range(8):
                    child = parent.readElement((Timestamp, SilentTracks, Position, PrevSize), parent=self)

                    if child is None:
                        break

                    prop = self.__ebmlpropertiesbyid__[child.ebmlID]
                    prop.__set__(self, child)

            parent.seek(self.offsetInBody + size)
            self.dataSize = size
            return self
        else:
            return super(Cluster, cls)._fromFile(file, size, ebmlID, parent)

    @property
    def segment(self):
        return self.parent

class Clusters(EBMLList):
    itemclass = Cluster

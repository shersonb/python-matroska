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
            EBMLProperty("offsetInSegment", int, optional=True),
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

    def iterPackets(self, start_pts=0, startPosition=0, trackNumber=None):
        """
        Create an iterator that yields packets contained in cluster.

        'start_pts' (in seconds): Starts iteration at first packet whose presentation timestamp is ≥ start_pts
        'startPosition' (in bytes): Starts demuxing at this offset inside cluster. Raises an exception if a child
            element does NOT start at this offset.
        'trackNumber': Filters by trackNumber. Can be either an integer or list/tuple of integers.
        """

        for block in self.iterBlocks(start_pts, startPosition=startPosition, trackNumber=trackNumber):
            for packet in block.iterPackets():
                yield packet

    def iterBlocks(self, start_pts=0, startPosition=0, trackNumber=None):
        """
        Create an iterator that yields blocks contained in cluster.

        'start_pts' (in seconds): Starts iteration at first block whose presentation timestamp is ≥ start_pts
        'startPosition' (in bytes): Starts demuxing at this offset inside cluster. Raises an exception if a child
            element does NOT start at this offset.
        'trackNumber': Filters by trackNumber. Can be either an integer or list/tuple of integers.
        """

        if hasattr(self, "_blocks"):
            for block in self.blocks:
                if block.pts*self.body.info.timestampScale >= start_pts*10**9:
                    break

            if trackNumber is None:
                yield block
            elif isinstance(trackNumber, (tuple, list)) and block.trackNumber in trackNumber:
                yield block
            elif block.trackNumber == trackNumber:
                yield block

            for block in self.blocks:
                if trackNumber is None:
                    yield block
                elif isinstance(trackNumber, (tuple, list)) and block.trackNumber in trackNumber:
                    yield block
                elif block.trackNumber == trackNumber:
                    yield block

        else:
            offset = max(startPosition, 0)

            while offset < self.dataSize:
                with self.body.lock:
                    self.body.seek(self.offsetInSegment + offset)
                    block = self.body.readElement(self._childTypes, parent=self)

                    if block is None:
                        raise ReadError("")

                    offset = self.body.tell() - self.offsetInSegment

                if isinstance(block, (matroska.blocks.SimpleBlock, matroska.blocks.BlockGroup)) \
                            and block.pts*self.body.info.timestampScale >= start_pts*10**9:
                    if trackNumber is None:
                        break

                    elif isinstance(trackNumber, (tuple, list)) and block.trackNumber in trackNumber:
                        break

                    elif block.trackNumber == trackNumber:
                        break

            yield block

            while offset < self.dataSize:
                with self.body.lock:
                    self.body.seek(self.offsetInSegment + offset)
                    block = self.body.readElement((matroska.blocks.SimpleBlock, matroska.blocks.BlockGroup), parent=self)

                    offset = self.body.tell() - self.offsetInSegment

                if block is not None:
                    if trackNumber is None:
                        yield block

                    elif isinstance(trackNumber, (tuple, list)) and block.trackNumber in trackNumber:
                        yield block

                    elif block.trackNumber == trackNumber:
                        yield block

    @classmethod
    def _fromFile(cls, file, size, ebmlID=None, parent=None):
        if file.seekable() and parent is not None:
            self = cls.__new__(cls)
            self._parent = parent

            with parent.lock:
                self.offsetInSegment = parent.tell()
                offset = 0

                for k in range(8):
                    child = parent.readElement((Timestamp, SilentTracks, Position, PrevSize), parent=self,
                                               ignore=(matroska.blocks.BlockGroup.ebmlID, matroska.blocks.SimpleBlock.ebmlID))

                    if child is None:
                        break

                    prop = self.__ebmlpropertiesbyid__[child.ebmlID]
                    prop.__set__(self, child)

            parent.seek(self.offsetInSegment + size)
            self.dataSize = size
            return self
        else:
            return super(Cluster, cls)._fromFile(file, size, ebmlID, parent)

    @property
    def segment(self):
        return self.parent

class Clusters(EBMLList):
    itemclass = Cluster

from ebml.base import EBMLMasterElement, EBMLInteger, EBMLProperty, EBMLList
from ebml.util import readVint, fromVint, parseElements
import matroska.blocks
import matroska.util
import threading
import gc

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

    #def __del__(self):
        #print(f"Deleting {self}")

class Cluster(EBMLMasterElement):
    ebmlID = b"\x1f\x43\xb6\x75"
    __ebmlchildren__ = (
            EBMLProperty("timestamp", Timestamp),
            EBMLProperty("silentTracks", SilentTracks, optional=True),
            EBMLProperty("position", Position, optional=True),
            EBMLProperty("prevSize", PrevSize, optional=True),
            EBMLProperty("blocks", Blocks, optional=True)
        )
    __ebmlproperties__ = (
            EBMLProperty("offsetInSegment", int, optional=True),
            EBMLProperty("dataSize", int, optional=True),
        )

    def __init__(self, timestamp, silentTracks=None, position=None, prevSize=None, blocks=None,
                 offsetInSegment=None, dataSize=None, readonly=False, parent=None):
        self.timestamp = timestamp
        self.silentTracks = silentTracks
        self.position = position
        self.prevSize = prevSize
        self.blocks = blocks
        self.offsetInSegment = offsetInSegment
        self.dataSize = dataSize
        self.parent = parent
        self._lock = threading.Lock()
        self._iterBlockCount = 0
        self.readonly = readonly

    def _size(self):
        if self.blocks is None and self.offsetInSegment:
            return self.dataSize

        return super()._size()

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

        blocks = self.iterBlocks(start_pts, startPosition=startPosition, trackNumber=trackNumber)

        try:
            for block in blocks:
                packets = block.iterPackets()

                for packet in packets:
                    yield packet

        finally:
            blocks.close()

    def iterBlocks(self, start_pts=0, startPosition=0, trackNumber=None):
        """
        Create an iterator that yields blocks contained in cluster.

        'start_pts' (in seconds): Starts iteration at first block whose presentation timestamp is ≥ start_pts
        'startPosition' (in bytes): Starts demuxing at this offset inside cluster. Raises an exception if a child
            element does NOT start at this offset.
        'trackNumber': Filters by trackNumber. Can be either an integer or list/tuple of integers.
        """

        with self._lock:
            blockswasnone = self.blocks is None
            if blockswasnone:
                if self.parent is not None:
                    self._loadBlocks()

                else:
                    return

            self._iterBlockCount += 1


        blocks = iter(self.blocks)

        try:
            for block in blocks:
                if block.pts*self.body.info.timestampScale >= start_pts*10**9:
                    break

            if trackNumber is None:
                yield block
            elif isinstance(trackNumber, (tuple, list)) and block.trackNumber in trackNumber:
                yield block
            elif block.trackNumber == trackNumber:
                yield block

            for block in blocks:
                if trackNumber is None:
                    yield block
                elif isinstance(trackNumber, (tuple, list)) and block.trackNumber in trackNumber:
                    yield block
                elif block.trackNumber == trackNumber:
                    yield block

        finally:
            with self._lock:
                self._iterBlockCount -= 1

                if blockswasnone and self._iterBlockCount == 0:
                    self._forgetBlocks()

    def _forgetBlocks(self):
        rostatus = self.readonly
        self._readonly = False
        self.blocks = None
        self._readonly = rostatus
        gc.collect()

    def _loadBlocks(self):
        data = self.parent.readbytes(self.offsetInSegment, self.dataSize)
        rostatus = self.readonly
        self._readonly = False
        self._timestamp = None
        self.silentTracks = None
        self.prevSize = None
        self.position = None
        self.blocks = []
        self._decodeData(data)
        self.readonly = rostatus

    @classmethod
    def _fromFile(cls, file, size, ebmlID=None, parent=None):
        if file.seekable() and parent is not None:
            self = cls.__new__(cls)
            self._parent = parent
            self._lock = threading.Lock()
            self._iterBlockCount = 0

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

    def _toBytes(self):
        if self.blocks is None and self.parent is not None:
            return self.parent.readbytes(self.dataOffsetInParent, self.dataSize)

        else:
            return super(Cluster, self)._toBytes()

    def toFile(self, file):
        if self.parent is not None:
            self.offsetInParent = self.parent.tell()

        super(Cluster, self).toFile(file)

    def _toFile(self, file):
        if self.parent is not None:
            self.dataOffsetInParent = self.parent.tell()
            self.dataSize = self._size()

            super(Cluster, self)._toFile(file)

            with self._lock:
                if self._iterBlockCount == 0:
                    self._forgetBlocks()
        else:
            super(Cluster, self)._toFile(file)

    @property
    def segment(self):
        return self.parent

    def scanBlocks(self):
        """Quick scan cluster for packets."""
        data = self.parent.readbytes(self.offsetInSegment, self.dataSize)
        timestampScale = self.segment.info.timestampScale

        for offset, ebmlID, sizesize, data in parseElements(data):
            dataSize = len(data)

            if ebmlID == matroska.blocks.SimpleBlock.ebmlID:
                (trackNumber, localpts, keyframe, invisible, discardable, lacing, data) = matroska.blocks.SimpleBlock.parsepkt(data)
                defaultDuration = self.segment.tracks.byTrackNumber[trackNumber].defaultDuration or 0

                if lacing == 0b10:
                    sizes, data = matroska.blocks.SimpleBlock.decodeFixedSizeLacing(data)

                elif lacing == 0b11:
                    sizes, data = matroska.blocks.SimpleBlock.decodeEBMLLacing(data)

                elif lacing == 0b01:
                    sizes, data = matroska.blocks.SimpleBlock.decodeXiphLacing(data)

                else:
                    sizes = []

                yield (offset, ebmlID, sizesize, dataSize, len(sizes) + 1, trackNumber, timestampScale*(self.timestamp + localpts),
                       defaultDuration, keyframe, invisible, discardable, None, None)

            elif ebmlID == matroska.blocks.BlockGroup.ebmlID:
                (trackNumber, localpts, duration, keyframe, invisible, discardable, lacing,
                        data, referencePriority, referenceBlocks) = matroska.blocks.BlockGroup.parsepkt(data)

                keyframe = not referenceBlocks and not discardable
                defaultDuration = self.segment.tracks.byTrackNumber[trackNumber].defaultDuration or 0

                if lacing == 0b10:
                    sizes, data = matroska.blocks.Block.decodeFixedSizeLacing(data)

                elif lacing == 0b11:
                    sizes, data = matroska.blocks.Block.decodeEBMLLacing(data)

                elif lacing == 0b01:
                    sizes, data = matroska.blocks.Block.decodeXiphLacing(data)

                else:
                    sizes = []

                if duration is None:
                    duration = defaultDuration

                else:
                    duration *= timestampScale

                yield (offset, ebmlID, sizesize, dataSize, len(sizes) + 1, trackNumber, timestampScale*(self.timestamp + localpts),
                       duration, keyframe, invisible, discardable, referencePriority, referenceBlocks)

    def scan(self):
        """Quick scan cluster for packets."""
        data = self.parent.readbytes(self.offsetInSegment, self.dataSize)
        timestampScale = self.segment.info.timestampScale

        for offset, ebmlID, sizesize, data in parseElements(data):
            if ebmlID == matroska.blocks.SimpleBlock.ebmlID:
                (trackNumber, localpts, keyframe, invisible, discardable, lacing, data) = matroska.blocks.SimpleBlock.parsepkt(data)
                defaultDuration = self.segment.tracks.byTrackNumber[trackNumber].defaultDuration or 0

                if lacing == 0b10:
                    sizes, data = matroska.blocks.SimpleBlock.decodeFixedSizeLacing(data)

                elif lacing == 0b11:
                    sizes, data = matroska.blocks.SimpleBlock.decodeEBMLLacing(data)

                elif lacing == 0b01:
                    sizes, data = matroska.blocks.SimpleBlock.decodeXiphLacing(data)

                else:
                    sizes = []

                for k, size in enumerate(sizes):
                    yield (offset, size, trackNumber, timestampScale*(self.timestamp + localpts) + k*defaultDuration,
                           defaultDuration, keyframe, invisible, discardable, None, None)

                yield (offset, len(data) - sum(sizes), trackNumber, timestampScale*(self.timestamp + localpts) + len(sizes)*defaultDuration,
                       defaultDuration, keyframe, invisible, discardable, None, None)

            elif ebmlID == matroska.blocks.BlockGroup.ebmlID:
                (trackNumber, localpts, duration, keyframe, invisible, discardable, lacing,
                        data, referencePriority, referenceBlocks) = matroska.blocks.BlockGroup.parsepkt(data)

                keyframe = not referenceBlocks and not discardable
                defaultDuration = self.segment.tracks.byTrackNumber[trackNumber].defaultDuration or 0

                if lacing == 0b10:
                    sizes, data = matroska.blocks.Block.decodeFixedSizeLacing(data)

                elif lacing == 0b11:
                    sizes, data = matroska.blocks.Block.decodeEBMLLacing(data)

                elif lacing == 0b01:
                    sizes, data = matroska.blocks.Block.decodeXiphLacing(data)

                else:
                    sizes = []

                if duration is None:
                    duration = defaultDuration

                else:
                    duration *= timestampScale

                for k, size in enumerate(sizes):
                    yield (offset, size, trackNumber, timestampScale*(self.timestamp + localpts) + k*defaultDuration,
                           duration, keyframe, invisible, discardable, referencePriority, referenceBlocks)

                yield (offset, len(data) - sum(sizes), trackNumber, timestampScale*(self.timestamp + localpts) + len(sizes)*defaultDuration,
                       duration, keyframe, invisible, discardable, referencePriority, referenceBlocks)



class Clusters(EBMLList):
    itemclass = Cluster

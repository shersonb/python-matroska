from ebml.base import EBMLMasterElement, EBMLData, EBMLInteger, EBMLElement, EBMLProperty, EBMLList
from ebml.util import parseVint, toVint, fromVint, formatBytes, parseElements
import traceback
import sys
import zlib

class intlist(EBMLList):
    itemclass = int

class Packet(object):
    trackNumber = EBMLProperty("trackNumber", int)
    data = EBMLProperty("data", bytes, optional=True)
    pts = EBMLProperty("pts", int, optional=True)
    duration = EBMLProperty("duration", int, optional=True)
    keyframe = EBMLProperty("keyframe", bool, optional=True)
    invisible = EBMLProperty("invisible", bool, optional=True)
    discardable = EBMLProperty("discardable", bool, optional=True)
    referenceBlocks = EBMLProperty("referenceBlocks", intlist, optional=True)
    readonly = EBMLElement.readonly

    @classmethod
    def fromAVPacket(cls, packet, trackNumber=None):
        trackNumber = trackNumber or packet.stream_index + 1
        return cls(trackNumber, data=packet.to_bytes(),
                   pts=int(10**9*packet.pts*packet.time_base), keyframe=packet.is_keyframe)

    @property
    def trackEntry(self):
        if self.parent:
            return self.parent.trackEntry

    @property
    def zdata(self):
        return self._zdata

    @zdata.setter
    def zdata(self, value):
        if self.data is None:
            if self.compression == 0:
                self.data = zlib.decompress(value)

        self._zdata = value

    @property
    def compression(self):
        return self._compression

    @compression.setter
    def compression(self, value):
        if self.readonly:
            raise AttributeError("Cannot change attribute for read-only element.")

        if value not in (None, 0):
            raise ValueError("Unsupported compression value.")

        if value == self._compression:
            return

        if self.data is not None:
            if value == 0:
                self.zdata = zlib.compress(self.data, level=9)
            else:
                self.zdata = None

        self._compression = value

    def __init__(self, trackNumber, data=None, zdata=None, compression=None, pts=None, duration=None,
                 keyframe=None, invisible=False, discardable=False, referenceBlocks=None, parent=None):
        self.trackNumber = trackNumber
        self.data = data
        self._compression = None
        self.compression = compression
        self.zdata = zdata
        self.pts = pts
        self.duration = duration
        self.keyframe = keyframe
        self.invisible = invisible
        self.discardable = discardable
        self.referenceBlocks = referenceBlocks
        self.parent = parent

    def __repr__(self):
        return f"Packet(trackNumber={self.trackNumber}, pts={self.pts}, duration={self.duration}, size={len(self.data)}, keyframe={self.keyframe})"

    @property
    def size(self):
        if self.compression is not None:
            return len(self.zdata)
        return len(self.data)

    @property
    def segment(self):
        return self.cluster.parent

    @property
    def cluster(self):
        return self.parent.cluster

    def copy(self, trackNumber=None, parent=None):
        """Create a copy of packet."""

        kwargs = dict(
                trackNumber=trackNumber or self.trackNumber,
                data=self.data,
                parent=parent
            )

        for attr in ("invisible", "discardable", "zdata", "compression",
                     "keyframe", "invisible", "discardable"):
            if hasattr(self, attr):
                kwargs[attr] = getattr(self, attr)

        if hasattr(self, "time_base") and self.time_base is not None:
            kwargs["pts"] = 10**9*self.pts*self.time_base
            kwargs["duration"] = 10**9*self.duration*self.time_base

            if hasattr(self, "referenceBlocks") and self.referenceBlocks is not None:
                kwargs["referenceBlocks"] = [int(10**9*ref*self.time_base) for ref in self.referenceBlocks]

        else:
            kwargs["pts"] = self.pts
            kwargs["duration"] = self.duration

            if hasattr(self, "referenceBlocks") and self.referenceBlocks is not None:
                kwargs["referenceBlocks"] = self.referenceBlocks

        return Packet(**kwargs)

class Packets(EBMLList):
    itemclass = Packet

class SimpleBlock(EBMLElement):
    ebmlID = b"\xa3"
    lacing = EBMLProperty("lacing", int, optional=True, default=0)
    __ebmlproperties__ = (
            EBMLProperty("trackNumber", int),
            EBMLProperty("localpts", int),
            EBMLProperty("packets", Packets),
            EBMLProperty("keyFrame", bool),
            lacing,
            EBMLProperty("invisible", bool, optional=True, default=False),
            EBMLProperty("discardable", bool, optional=True, default=False),
        )

    @lacing.sethook
    def lacing(self, value):
        if value < 0 or value >= 4:
            raise ValueError("Invalid value for lacing. Must be 0b00, 0b01, 0b10, or 0b11.")

        return value

    @property
    def cluster(self):
        return self.parent

    @property
    def trackEntry(self):
        if self.body is not None and self.body.tracks is not None:
            return self.body.tracks.byTrackNumber[self.trackNumber]

    @property
    def parent(self):
        if hasattr(self, "_parent"):
            return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        self.ancestorChanged()

    def ancestorChanged(self):
        if None not in (self.cluster, self.segment, self.duration):
            for k, packet in enumerate(self.packets):
                try:
                    packet.pts = self.cluster.timestamp*self.segment.info.timestampScale + self.localpts*self.segment.info.timestampScale + k*self.duration/len(self.packets)
                except AttributeError:
                    return
                packet.duration = self.duration/len(self.packets)

    @property
    def pktduration(self):
        return self.trackEntry.defaultDuration

    @property
    def duration(self):
        if self.pktduration:
            return len(self.packets)*self.pktduration

    @property
    def segment(self):
        if self.cluster is not None:
            return self.cluster.parent

    @property
    def pts(self):
        if self.cluster is not None:
            return self.localpts + self.cluster.timestamp

    @staticmethod
    def sizeXiphLacing(sizes):
        Sizes = [1]

        for size in sizes:
            q, r = divmod(size, 255)
            Sizes.append(q + 1)

        return sum(Sizes)

    @staticmethod
    def sizeEBMLLacing(sizes):
        Sizes = [1, len(toVint(sizes[0]))]

        for s1, s2 in zip(sizes[:-1], sizes[1:]):
            for k in range(1, 9):
                if -2**(7*k - 1) < s2 - s1 < 2**(7*k - 1):
                    Sizes.append(k)
                    break
            else:
                raise OverflowError

        return sum(Sizes)

    def _size(self):
        if self.trackEntry is not None:
            compression = self.trackEntry.compression

            for packet in self.packets:
                if packet.compression != compression:
                    packet.compression = compression

            pktsizes = [pkt.size for pkt in self.packets]
        else:
            compression = None
            pktsizes = [len(pkt.data) for pkt in self.packets]

        trackNumberSize = len(toVint(self.trackNumber))
        localptsSize = 2
        flagsSize = 1

        if len(self.packets) > 1:
            if self.lacing == 0:
                raise ValueError("Multiple packets requires lacing set to non-zero value.")

            if self.lacing == 0b10:
                if min(pktsizes) != max(pktsizes):
                    raise ValueError("Packets with different sizes incompatible with lacing=0b10 (fixed-size lacing).")

                lacingdataSize = 1

            elif self.lacing == 0b11:
                lacingdataSize = self.sizeEBMLLacing(pktsizes[:-1])

            elif self.lacing == 0b01:
                lacingdataSize = self.sizeXiphLacing(pktsizes[:-1])

        else:
            lacingdataSize = 0

        return trackNumberSize + localptsSize + flagsSize + lacingdataSize + sum(pktsizes)

    def __repr__(self):
        params = []
        for param in dir(type(self)):
            if param == "parent":
                continue
            if isinstance(getattr(type(self), param), EBMLProperty):
                try:
                    value = getattr(self, param)
                except AttributeError:
                    continue
                if value is None:
                    continue
                if isinstance(value, EBMLMasterElement):
                    params.append(f"{param}={value.__class__.__name__}(...)")
                elif isinstance(value, EBMLList):
                    if isinstance(value.itemclass, tuple):
                        classes = "|".join(cls.__name__ for cls in value.itemclass)
                        params.append(f"{param}=[({classes})(...), ...]")
                    else:
                        params.append(f"{param}=[{value.itemclass.__name__}(...), ...]")
                else:
                    params.append(f"{param}={value}")
        params = ", ".join(params)
        return f"{self.__class__.__name__}({params})"

    @staticmethod
    def decodeFixedSizeLacing(data):
        n = data[0] + 1
        size, r = divmod(len(data) - 1, n)

        if r:
            raise ValueError("Data size not evenly divisble by number of blocks!")

        return [data[j:j+size] for j in range(1, len(data), size)]

    @staticmethod
    def decodeFixedSizeLacing(data):
        n = data[0] + 1
        size, r = divmod(len(data) - 1, n)

        if r:
            raise ValueError("Data size not evenly divisble by number of blocks!")

        return ((size,)*(n - 1), data[1:])

    @staticmethod
    def decodeXiphLacing(data):
        n = data[0] + 1
        data = data[1:]

        sizes = []

        for k in range(n - 1):
            j = 0

            while data[0] == 255:
                data = data[1:]
                j += 1

            sizes.append(255*j + data[0])
            data = data[1:]

        return sizes, data

    @staticmethod
    def decodeEBMLLacing(data):
        n = data[0] + 1
        data = data[1:]

        size, data = parseVint(data)
        sizes = [fromVint(size)]

        for k in range(n - 2):
            size, data = parseVint(data)
            sizes.append(sizes[-1] + fromVint(size) - 2**(7*len(size) - 1) + 1)

        return sizes, data

    @staticmethod
    def parsepkt(data):
        """
        Parse data.

        Returns a tuple: (trackNumber, localpts, keyframe, invisible, discardable, lacing, numberInLace, lacedData)
        """
        trackNumber, data = parseVint(data)
        localpts = int.from_bytes(data[:2], "big", signed=True)
        flags = data[2]
        keyframe = bool(flags & 0b10000000)
        invisible = bool(flags & 0b00001000)
        discardable = (flags & 0b00000001)
        lacing = (flags & 0b00000110) >> 1
        return (fromVint(trackNumber), localpts, keyframe, invisible, discardable, lacing, data[3:])

    @classmethod
    def _fromBytes(cls, data, parent=None):
        self = cls.__new__(cls)
        self._parent = parent

        (self.trackNumber, self.localpts, self.keyFrame, self.invisible,
         self.discardable, self.lacing, data) = self.parsepkt(data)

        trackEntry = self.trackEntry

        if trackEntry is not None:
            compression = trackEntry.compression
        else:
            compression = None

        self.packets = Packets([], parent=self)

        if self.lacing == 0b10:
            sizes, data = self.decodeFixedSizeLacing(data)

        elif self.lacing == 0b11:
            sizes, data = self.decodeEBMLLacing(data)

        elif self.lacing == 0b01:
            sizes, data = self.decodeXiphLacing(data)

        else:
            sizes = []

        chunks = []

        for size in sizes:
            chunks.append(data[:size])
            data = data[size:]

        chunks.append(data)

        for k, chunk in enumerate(chunks):
            if self.trackEntry is not None and self.trackEntry.defaultDuration is not None and self.pktduration is not None:
                pts = self.pts*self.body.info.timestampScale + k*self.pktduration

            else:
                pts = self.pts*self.body.info.timestampScale

            if compression is not None:
                pkt = Packet(self.trackNumber, zdata=chunk, compression=compression, keyframe=self.keyFrame,
                             pts=pts, duration=self.pktduration, parent=self)

            else:
                pkt = Packet(self.trackNumber, data=chunk, keyframe=self.keyFrame,
                             pts=pts, duration=self.pktduration, parent=self)

            pkt.readonly = True
            self.packets.append(pkt)

        return self

    @staticmethod
    def encodeXiphLacing(sizes):
        lacingdata = len(sizes).to_bytes(1, "big")

        for size in sizes:
            q, r = divmod(size, 255)
            lacingdata += b"\xff"*q + r.to_bytes(1, "big")

        return lacingdata

    @staticmethod
    def encodeEBMLLacing(sizes):
        lacingdata = len(sizes).to_bytes(1, "big") + toVint(sizes[0])

        for s1, s2 in zip(sizes[:-1], sizes[1:]):
            for k in range(1, 9):
                if -2**(7*k - 1) < s2 - s1 < 2**(7*k - 1):
                    lacingdata += toVint(s2 - s1+ 2**(7*k - 1) - 1)
                    break
            else:
                raise OverflowError

        return lacingdata

    def _toBytes(self):
        trackEntry = self.trackEntry

        if trackEntry is not None:
            compression = trackEntry.compression

            for pkt in self.packets:
                if pkt.compression != compression:
                    pkt.compression = compression

        else:
            compression = None

        trackNumber = toVint(self.trackNumber)
        localpts = self.localpts.to_bytes(2, "big", signed=True)

        if len(self.packets) > 1:
            flags = (self.keyFrame << 7 | self.invisible << 3 | self.lacing << 1 | self.discardable << 0).to_bytes(1, "big")
            if self.lacing == 0b00:
                raise ValueError("Multiple packets requires lacing set to non-zero value.")

            sizes = [pkt.size for pkt in self.packets]

            if self.lacing == 0b10:
                if min(sizes) != max(sizes):
                    raise ValueError("Packets with different sizes incompatible with lacing=0b10 (fixed-size lacing).")

                lacingdata = (len(self.packets) - 1).to_bytes(1, "big")

            elif self.lacing == 0b11:
                lacingdata = self.encodeEBMLLacing(sizes[:-1])

            elif self.lacing == 0b01:
                lacingdata = self.encodeXiphLacing(sizes[:-1])

        else:
            flags = (self.keyFrame << 7 | self.invisible << 3 |  self.discardable << 0).to_bytes(1, "big")
            lacingdata = b""

        if compression is not None:
            return trackNumber + localpts + flags + lacingdata + b"".join([pkt.zdata for pkt in self.packets])

        return trackNumber + localpts + flags + lacingdata + b"".join([pkt.data for pkt in self.packets])

    def _write(self, file):
        file.write(self._unhook())

    def iterPackets(self):
        for packet in self.packets:
            packet = packet.copy(parent=self)
            packet.invisible = self.invisible
            packet.discardable = self.discardable
            yield packet

def hh(data):
    return " ".join([f"{x:02x}" for x in data])

def bb(data):
    return " ".join([f"{x:08b}" for x in data])

class Block(SimpleBlock):
    ebmlID = b"\xa1"

    @property
    def cluster(self):
        if self.parent is not None:
            return self.parent.parent

    @property
    def segment(self):
        if self.cluster is not None:
            return self.cluster.parent

    @property
    def pktduration(self):
        if None not in (self.parent, self.segment) and self.parent.blockDuration is not None:
            return self.parent.blockDuration*self.segment.info.timestampScale

    @property
    def duration(self):
        if None not in (self.parent, self.segment) and self.parent.blockDuration is not None:
            return self.parent.blockDuration*self.segment.info.timestampScale

    @staticmethod
    def parsepkt(data):
        """
        Parse data.

        Returns a tuple: (trackNumber, localpts, keyframe, invisible, discardable, lacing, numberInLace, lacedData)
        """
        trackNumber, data = parseVint(data)
        localpts = int.from_bytes(data[:2], "big", signed=True)
        flags = data[2]
        keyframe = False
        invisible = bool(flags & 0b00001000)
        discardable = (flags & 0b00000001)
        lacing = (flags & 0b00000110) >> 1

        return (fromVint(trackNumber), localpts, keyframe, invisible, discardable, lacing, data[3:])

    #parsepkt = matroska.util.parseBlock

class BlockAdditional(SimpleBlock):
    ebmlID = b"\xa5"

class BlockAddID(EBMLInteger):
    ebmlID = b"\xee"

class BlockMore(EBMLMasterElement):
    ebmlID = b"\xa6"
    __ebmlchildren__ = (
            EBMLProperty("blockAdditional", BlockAdditional),
            EBMLProperty("blockAddID", BlockAddID, "value"),
        )

class BlockMores(EBMLList):
    itemclass = BlockMore


class BlockAdditions(EBMLMasterElement):
    ebmlID = b"\x75\xa1"
    __ebmlchildren__ = (EBMLProperty("blockMores", BlockMores),)

class BlockDuration(EBMLInteger):
    ebmlID = b"\x9b"

class ReferencePriority(EBMLInteger):
    ebmlID = b"\xfa"

class ReferenceBlock(EBMLInteger):
    ebmlID = b"\xfb"
    signed = True

class ReferenceBlocks(EBMLList):
    itemclass = ReferenceBlock

class CodecState(EBMLData):
    ebmlID = b"\xa4"

class DiscardPadding(EBMLInteger):
    ebmlID = b"\x75\xa2"
    signed = True

class Slices(EBMLData):
    ebmlID = b"\x8e"


class BlockGroup(EBMLMasterElement):
    ebmlID = b"\xa0"
    blockDuration = EBMLProperty("blockDuration", BlockDuration, optional=True)
    __ebmlchildren__ = (
            EBMLProperty("block", Block),
            EBMLProperty("referencePriority", ReferencePriority, optional=True),
            blockDuration,
            EBMLProperty("blockAdditions", BlockAdditions, optional=True),
            EBMLProperty("referenceBlocks", ReferenceBlocks, optional=True),
            EBMLProperty("codecState", CodecState, optional=True),
            EBMLProperty("discardPadding", DiscardPadding, optional=True),
            EBMLProperty("slices", Slices, optional=True),
        )

    def iterPackets(self):
        for packet in self.block.iterPackets():
            packet = packet.copy(parent=self.block)

            if self.blockDuration is not None and self.segment.info.timestampScale is not None:
                packet.duration = self.blockDuration*self.segment.info.timestampScale

                if self.referenceBlocks:
                    packet.referenceBlocks = [dt*self.segment.info.timestampScale for dt in self.referenceBlocks]

            packet.readonly = True
            yield packet

    @property
    def pts(self):
        return self.block.pts

    @property
    def trackNumber(self):
        return self.block.trackNumber

    @property
    def cluster(self):
        return self.parent

    @property
    def segment(self):
        return self.cluster.parent

    @property
    def parent(self):
        if hasattr(self, "_parent"):
            return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value
        self.ancestorChanged()

    def ancestorChanged(self):
        if hasattr(self, "_block"):
            self.block.ancestorChanged()

    @staticmethod
    def parsepkt(data):
        """
        Parse data.

        Returns a tuple: (trackNumber, localpts, keyframe, invisible, discardable, lacing, numberInLace, lacedData, referencePriority, referenceBlocks)
        """
        referenceBlocks = []
        referencePriority = None
        duration = None

        for offset, ebmlID, sizesize, data in parseElements(data):
            if ebmlID == Block.ebmlID:
                (trackNumber, localpts, keyframe, invisible, discardable, lacing, pktdata) = Block.parsepkt(data)

            elif ebmlID == ReferencePriority.ebmlID:
                referencePriority = int.from_bytes(data, "big")

            elif ebmlID == ReferenceBlock.ebmlID:
                referenceBlocks.append(int.from_bytes(data, "big", signed=True))

            elif ebmlID == BlockDuration.ebmlID:
                duration = int.from_bytes(data, "big")

        return (trackNumber, localpts, duration, keyframe, invisible, discardable, lacing, pktdata, referencePriority, referenceBlocks)

class Blocks(EBMLList):
    itemclass = (SimpleBlock, BlockGroup)

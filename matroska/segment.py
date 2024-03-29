from ebml.base import EBMLInteger, EBMLString, EBMLMasterElement, EBMLElement, Void, EBMLList, EBMLProperty
from ebml.util import peekVint, fromVint
from ebml.document import EBMLBody
from ebml import __version__ as ebmlversion

from .version import __version__ as mkvversion
from .seekhead import SeekHead, Seek
from .info import Info
from .tracks import Tracks
from .chapters import Chapters
from .attachments import Attachments
from .cluster import Cluster, Clusters
from .cues import Cues, CueTrackPositions, CuePoint
from .tags import Tag, Tags, Targets, SimpleTag
from .blocks import Packet, Block, BlockGroup, SimpleBlock

import sys
import random
import threading
import time
import gc

__all__ = ["Segment"]

class Segment(EBMLBody):
    ebmlID = b"\x18\x53\x80\x67"
    __ebmlchildren__ = (
            EBMLProperty("seekHead", SeekHead),
            EBMLProperty("info", Info),
            EBMLProperty("tracks", Tracks),
            EBMLProperty("chapters", Chapters, optional=True),
            EBMLProperty("attachments", Attachments, optional=True),
            #EBMLProperty("clusters", Clusters),
            EBMLProperty("cues", Cues, optional=True),
            EBMLProperty("tags", Tags, optional=True),
         )

    _childTypes = {Cluster.ebmlID: Cluster}

    allowunknown = False

    def __init__(self, file, parent=None):
        self._clustersByOffset = {}
        self._clustersByTimestamp = {}
        self._lastClusterEnd = None
        self._currentCluster = None
        self._currentBlocks = {}
        self._blocksToIndex = set()
        self._packetsMuxed = 0
        self._trackPackets = {}
        self._trackBytes = {}
        self._trackDurations = {}
        self._seekHead = None
        self._seekHeadOffset = None
        super(Segment, self).__init__(file, parent=parent)

    @property
    def infoOffset(self):
        for seek in self.seekHead.seeks:
            if seek.seekID == self.info.ebmlID:
                return seek.seekPosition

    @property
    def chaptersOffset(self):
        if self.chapters:
            for seek in self.seekHead.seeks:
                if seek.seekID == self.chapters.ebmlID:
                    return seek.seekPosition

    @property
    def attachmentsOffset(self):
        if self.attachments:
            for seek in self.seekHead.seeks:
                if seek.seekID == self.attachments.ebmlID:
                    return seek.seekPosition

    def _init_read(self):
        super(Segment, self)._init_read()

        while self.tell() < min(4*1024**2, self._contentssize):
            offset = self.tell()
            child = self.readChildElement()

            if isinstance(child, SeekHead):
                if self._file.writable():
                    child = child.copy(parent=self)

                self.seekHead = child
                break

        offset = self.tell()

        if self.seekHead:
            for seek in self.seekHead.seeks:
                for prop in self.__ebmlchildren__:
                    if prop.cls.ebmlID == seek.seekID:
                        try:
                            attributeDNE = prop.__get__(self) is None
                        except AttributeError:
                            attributeDNE = True
                        if attributeDNE:
                            self.seek(seek.seekPosition)
                            prop.__set__(self, self.readChildElement())

        self.seek(0)
        self.scan()

    def _init_write(self):
        self.seekHead = SeekHead([], parent=self)

        self.info = Info(timestampScale=10**6, writingApp="",
                                       muxingApp=f"Python {sys.version}; python-matroska {mkvversion}; python-ebml {ebmlversion}",
                                       parent=self)

        self.tracks = Tracks([], parent=self)
        self.chapters = Chapters([], parent=self)
        self.attachments = Attachments([], parent=self)
        self.cues = Cues([])
        self.tags = Tags([])

        super(Segment, self)._init_write()

    def findCue(self, start_pts=0, trackNumber=None):
        """
        Attempts to find CuePoint element.
        """

        if self.cues is None:
            return

        cuePoint = None

        for cuePoint2 in self.cues.cuePoints:
            for cueTrackPosition in cuePoint2.cueTrackPositionsList:
                if trackNumber is None or cueTrackPosition.cueTrack == trackNumber:
                    break
            else:
                continue

            if cuePoint2.cueTime > 10**9*start_pts/self.info.timestampScale:
                return cuePoint

            cuePoint = cuePoint2

        return cuePoint

    def readbytes(self, offset, size):
        with self.lock:
            current = self.tell()
            self.seek(offset)
            data = self._file.read(size)
            self.seek(current)

        return data

    def readChildElement(self):
        offset = self.tell()
        child = super().readChildElement()

        if isinstance(child, Cluster):
            self._clustersByOffset[child.offsetInSegment] = child
            self._clustersByTimestamp[child.timestamp] = child

        if isinstance(child, SeekHead):
            self._seekHeadOffset = offset

        return child

    def readCluster(self):
        childTypes = list(self._childTypes.keys())
        childTypes.remove(Cluster.ebmlID)
        return self.readElement(Cluster, parent=self, ignore=childTypes)

    def writeChildElement(self, child):
        offset = super().writeChildElement(child)

        if isinstance(child, Cluster):
            self._clustersByOffset[offset] = child
            self._clustersByTimestamp[child.timestamp] = child

        if isinstance(child, (Info, Tracks,
                              Attachments, Cues,
                              Tags, Chapters)):
            for seek in list.copy(self.seekHead.seeks):
                if seek.seekID == child.ebmlID:
                    seek.seekPosition = offset
                    break

            else:
                self.seekHead.seeks.append(Seek(seekID=child.ebmlID, seekPosition=offset))

        return offset

    def deleteChildElement(self, offset):
        super().deleteChildElement(offset)

        for seek in list.copy(self.seekHead.seeks):
            if seek.seekPosition == offset:
                self.seekHead.seeks.remove(seek)

        if offset in self._clustersByOffset:
            cluster = self._clustersByOffset.pop(offset)
            del self._clustersByTimestamp[cluster.timestamp]

            for cuePoint in list.copy(self.cues.cuePoints):
                for cueTrackPositions in list.copy(cuePoint.cueTrackPositionsList):
                    if cueTrackPositions.cueClusterPosition == offset:
                        cuePoint.cueTrackPositionsList.remove(cueTrackPositions)

                if len(cuePoint.cueTrackPositionsList) == 0:
                    self.cues.cuePoints.remove(cuePoint)

    def iterClusters(self, start_pts=0, startClusterPosition=None, trackNumber=None):
        if startClusterPosition is None:
            try:
                cuePoint = self.findCue(start_pts, trackNumber)

            except AttributeError:
                cuePoint = None

            if cuePoint is not None:
                for cueTrackPosition in cuePoint.cueTrackPositionsList:
                    if trackNumber is None or cueTrackPosition.cueTrack == trackNumber:
                        break

                offset = cueTrackPosition.cueClusterPosition

            else:
                offset = 0

        else:
            offset = startClusterPosition

        cutoff = 10**9*start_pts/self.info.timestampScale - 32768

        while offset < self._contentssize:
            with self.lock:
                self.seek(offset)
                cluster = self.readCluster()
                offset = self.tell()

            if cluster:
                if cluster.timestamp < cutoff:
                    continue

                yield cluster

    def iterPackets(self, start_pts=0, startClusterPosition=None, startBlockPosition=0, trackNumber=None):
        """
        Create an iterator that yields packets contained in segment.

        'start_pts' (in seconds): Starts iteration at first packet whose presentation timestamp is ≥ start_pts
        'startClusterPosition' (in bytes): Starts demuxing from cluster at this position. Raises an exception if a child
            element does NOT start at this offset.
        'startBlockPosition' (in bytes): Starts demuxing at this offset inside the first cluster. Raises an exception if a child
            element does NOT start at this offset.
        'trackNumber': Filters by trackNumber. Can be either an integer or list/tuple of integers.

        Both 'startClusterPosition' and 'startBlockPosition' are values that can be looked up in the Cues element
        (from the CueClusterPosition and CueRelativePosition elements). See 'self.findCue'.
        """

        clusters = self.iterClusters(start_pts, startClusterPosition=startClusterPosition, trackNumber=trackNumber)

        for k, cluster in enumerate(clusters):
            if k == 0:
                packets = cluster.iterPackets(start_pts=start_pts, startPosition=startBlockPosition, trackNumber=trackNumber)

            else:
                packets = cluster.iterPackets(start_pts=start_pts, trackNumber=trackNumber)

            for packet in packets:
                yield packet

    def writeCluster(self):
        clusterOffset = self._lastClusterEnd or self.tell()

        inClusterOffset = 0

        for item in self._currentCluster.iterchildren():
            if item in self._blocksToIndex:
                cueTrackPositions = CueTrackPositions(cueClusterPosition=clusterOffset,
                                                                    cueRelativePosition=inClusterOffset, cueTrack=item.trackNumber)

                cuePoint = CuePoint(cueTime=item.pts, cueTrackPositionsList=[cueTrackPositions])
                self.cues.cuePoints.append(cuePoint)

            inClusterOffset += item.size()

        with self.lock:
            n = self.infoOffset

            if n in self._knownChildren:
                self.deleteChildElement(n)

            self.seek(n)
            self.writeChildElement(self.info.copy())
            self.seek(clusterOffset)
            self._lastClusterEnd = clusterOffset + self._currentCluster.size()
            self.writeChildElement(self._currentCluster)
            self.flush()

        self._currentCluster = None
        self._currentBlocks.clear()
        self._blocksToIndex.clear()
        gc.collect()

    def _newBlockGroup(self, trackNumber):
        pass

    def _init_mux(self):
        self.seek(128)
        self.writeChildElement(self.info.copy())
        self.seek(128, 1)
        self.writeChildElement(self.tracks)

        if len(self.chapters.editionEntries):
            self.writeChildElement(self.chapters)

        elif not self.chapters.readonly:
            self.chapters.readonly = True

        if len(self.attachments.attachedFiles):
            self.writeChildElement(self.attachments)

        elif not self.attachments.readonly:
            self.attachments.readonly = True

        self.flush()

        self._trackPackets = {track.trackNumber: 0 for track in self.tracks.trackEntries}
        self._trackBytes = {track.trackNumber: 0 for track in self.tracks.trackEntries}
        self._trackDurations = {track.trackNumber: 0 for track in self.tracks.trackEntries}

    def mux(self, packet, newcluster=False, cuepoint=False):
        """
        Writes a packet to file. Automatically handles creation of Cluster, SimpleBlock, BlockGroup+Block
        elements.

        Specify newcluster=True to force creation of new Cluster.

        Specify cuepoint=True to force creation of a CuePoint.

        Returns number of bytes written, accounting for compression,
        excluding BlockGroup+Block/SimpleBlock overhead.
        """

        if not isinstance(packet, Packet):
            packet = Packet.copy(packet)

        timestampScale = self.info.timestampScale

        trackEntry = self.tracks.byTrackNumber[packet.trackNumber]

        defaultDuration = trackEntry.defaultDuration
        packet.compression = trackEntry.compression
        maxInLace = trackEntry.maxInLace if trackEntry.maxInLace is not None else 8

        packetDuration = packet.duration or defaultDuration or None

        isDefaultDuration = defaultDuration is not None and (not packetDuration or abs(defaultDuration - packetDuration) <= 2)

        isVideoKeyframe = trackEntry.video is not None and packet.keyframe

        isSubtitle = trackEntry.trackType == 17

        nonemptyCluster = self._currentCluster is not None and len(self._currentCluster.blocks)
        ptsOverflow = nonemptyCluster and abs(int(packet.pts/timestampScale - \
                                              self._currentCluster.timestamp)) >= 2**15

        newClusterNeeded = (nonemptyCluster and (isVideoKeyframe or ptsOverflow or newcluster)
                            and packet.pts > self._currentCluster.timestamp*timestampScale)

        if self._packetsMuxed == 0:
            self._init_mux()
            self._currentCluster = Cluster(timestamp=int(packet.pts/timestampScale),
                                                        blocks=[], parent=self)

        if newClusterNeeded:
            self.writeCluster()
            self._currentCluster = Cluster(timestamp=int(packet.pts/timestampScale),
                                                            blocks=[], parent=self)

        localpts = int(packet.pts/timestampScale - self._currentCluster.timestamp + 0.01)

        if not isDefaultDuration or packet.referenceBlocks:
            """Use BlockGroup/Block"""
            block = Block(trackNumber=packet.trackNumber, localpts=localpts,
                                                packets=[packet], keyFrame=packet.keyframe, lacing=0,
                                                invisible=packet.invisible, discardable=packet.discardable)

            if packet.referenceBlocks:
                referenceBlocks = [int((packet.pts + ref)/timestampScale - self._currentCluster.timestamp) - localpts for ref in packet.referenceBlocks]

            else:
                referenceBlocks = None

            blockDuration = packetDuration and int(packetDuration/timestampScale)
            blockgroup = BlockGroup(block=block, referenceBlocks=referenceBlocks,
                                                    blockDuration=blockDuration, parent=self._currentCluster)

            self._currentCluster.blocks.append(blockgroup)

            if trackEntry in self._currentBlocks:
                del self._currentBlocks[trackEntry]

            if isVideoKeyframe or isSubtitle or cuepoint:
                self._blocksToIndex.add(blockgroup)

        elif not trackEntry.flagLacing:
            block = SimpleBlock(trackNumber=packet.trackNumber, localpts=localpts,
                                                packets=[packet], keyFrame=packet.keyframe, lacing=0,
                                                invisible=packet.invisible, discardable=packet.discardable,
                                                parent=self._currentCluster)

            self._currentCluster.blocks.append(block)

            if isVideoKeyframe or isSubtitle or cuepoint:
                self._blocksToIndex.add(block)

        elif trackEntry in self._currentBlocks and len(self._currentBlocks[trackEntry].packets) < maxInLace:
            block = self._currentBlocks[trackEntry]

            if block.packets[-1].size != packet.size:
                block.lacing = 0b11

            block.packets.append(packet)
            packet.parent = block

        else:
            block = SimpleBlock(trackNumber=packet.trackNumber,
                                                localpts=localpts, packets=[packet],
                                                keyFrame=packet.keyframe, lacing=0b10, parent=self._currentCluster)

            self._currentCluster.blocks.append(block)
            self._currentBlocks[trackEntry] = block

            if isVideoKeyframe or isSubtitle or cuepoint:
                self._blocksToIndex.add(blockgroup)

        self._packetsMuxed += 1
        self._trackPackets[trackEntry.trackNumber] += 1
        self._trackBytes[trackEntry.trackNumber] += packet.size

        if packet.pts is not None:
            packet_end = float(packet.pts + (packetDuration or 0))

            currentDuration = self.info.duration

            if currentDuration is not None:
                self.info.duration = max(currentDuration, packet_end/timestampScale)

            else:
                self.info.duration = packet_end/timestampScale

            currentTrackDuration = self._trackDurations.get(trackEntry.trackNumber, 0)
            self._trackDurations[trackEntry.trackNumber] = max(currentTrackDuration, packet_end/10**9)

        return packet.size

    def makeStatsTags(self):
        for track in self.tracks.trackEntries:
            size = self._trackBytes.get(track.trackNumber, 0)
            duration = self._trackDurations.get(track.trackNumber, 0)
            n = self._trackPackets.get(track.trackNumber, 0)

            simpleTags = []
            if duration:
                bps = int(8*size/duration+0.5)
                simpleTags.append(SimpleTag(tagLanguage="eng",
                                                        tagName="BPS", tagString=f"{bps:d}"))

            m, s = divmod(duration, 60)
            m = int(m)
            s = float(s)
            h, m = divmod(m, 60)
            simpleTags.append(SimpleTag(tagLanguage="eng",
                                                      tagName="DURATION", tagString=f"{h:d}:{m:02d}:{s:012.9f}"))
            simpleTags.append(SimpleTag(tagLanguage="eng",
                                                      tagName="NUMBER_OF_FRAMES", tagString=f"{n}"))
            simpleTags.append(SimpleTag(tagLanguage="eng",
                                                      tagName="NUMBER_OF_BYTES", tagString=f"{size}"))
            simpleTags.append(SimpleTag(tagLanguage="eng",
                                                      tagName="_STATISTICS_WRITING_APP", tagString=f"python {sys.version}"))
            simpleTags.append(SimpleTag(tagLanguage="eng",
                                                      tagName="_STATISTICS_TAGS", tagString="BPS DURATION NUMBER_OF_BYTES NUMBER_OF_FRAMES"))
            targets = Targets(tagTrackUIDs=[track.trackUID], targetType="MOVIE", targetTypeValue=50)
            tag = Tag(simpleTags=simpleTags, targets=targets)
            self.tags.tagList.append(tag)

    def close(self):
        if self._file.writable():
            if self._currentCluster is not None:
                self.writeCluster()

            self.seek(max(self.tell(), 128))

            if self.cues not in self.seekHead:
                self.writeChildElement(self.cues)

            if self.tags not in self.seekHead and \
                (self._trackBytes or self._trackDurations or self._trackPackets):
                self.makeStatsTags()
                self.writeChildElement(self.tags)

            if self._modified:
                if self._seekHeadOffset is not None:
                    self.deleteChildElement(self._seekHeadOffset)
                    self.seek(self._seekHeadOffset)

                else:
                    self.seek(0)

                self.writeChildElement(self.seekHead)

        super().close()

    @property
    def packetsMuxed(self):
        return self._packetsMuxed

    @property
    def clusterCount(self):
        return len(self._clustersByOffset)

    @property
    def firstClusterOffset(self):
        return min(self._clustersByOffset.keys())

    @property
    def lastClusterEnd(self):
        return self._lastClusterEnd


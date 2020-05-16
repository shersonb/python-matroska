from ebml.base import EBMLInteger, EBMLString, EBMLMasterElement, EBMLElement, Void, EBMLList, EBMLProperty
from ebml.util import peekVint, fromVint
#from ebml.util import ebmlproperty as EBMLProperty

import matroska
import matroska.seekhead
import matroska.info
import matroska.tracks
import matroska.chapters
import matroska.attachments
import matroska.cluster
import matroska.cues
import matroska.tags
import ebml
import sys
import random
import threading
import time

__all__ = ["SegmentReader"]

class Segment(ebml.document.EBMLBody):
    ebmlID = b"\x18\x53\x80\x67"
    __ebmlchildren__ = (
            EBMLProperty("seekHead", matroska.seekhead.SeekHead),
            EBMLProperty("info", matroska.info.Info),
            EBMLProperty("tracks", matroska.tracks.Tracks),
            EBMLProperty("chapters", matroska.chapters.Chapters, optional=True),
            EBMLProperty("attachments", matroska.attachments.Attachments, optional=True),
            #EBMLProperty("clusters", matroska.cluster.Clusters),
            EBMLProperty("cues", matroska.cues.Cues, optional=True),
            EBMLProperty("tags", matroska.tags.Tags, optional=True),
         )

    _childTypes = {matroska.cluster.Cluster.ebmlID: matroska.cluster.Cluster}

    allowunknown = False

    def __init__(self, file, parent=None):
        super(Segment, self).__init__(file, parent=parent)
        self._clustersByTimestamp = {}
        self._clustersByOffset = {}
        self._currentCluster = None
        self._currentBlocks = {}
        self._blocksToIndex = set()
        self._infoOffset = None
        self._packetsMuxed = 0
        self._trackPackets = {}
        self._trackBytes = {}
        self._trackDurations = {}


    def _init_read(self):
        super(Segment, self)._init_read()

        while self.tell() < min(4*1024**2, self._contentssize):
            offset = self.tell()
            child = self.readChildElement()

            if isinstance(child, matroska.seekhead.SeekHead):
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

    def _init_write(self):
        self.seekHead = matroska.seekhead.SeekHead([], parent=self)

        self.info = matroska.info.Info(timestampScale=10**6, writingApp="",
                                       muxingApp=f"Python {sys.version}; python-matroska {matroska.__version__}; python-ebml {ebml.__version__}",
                                       parent=self)

        self.tracks = matroska.tracks.Tracks([], parent=self)
        self.chapters = matroska.chapters.Chapters([], parent=self)
        self.attachments = matroska.attachments.Attachments([], parent=self)
        self.cues = matroska.cues.Cues([])
        self.tags = matroska.tags.Tags([])

        super(Segment, self)._init_write()

    def findCue(self, start_pts=0, trackNumber=None):
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

    def readChildElement(self):
        child = super().readChildElement()

        if isinstance(child, matroska.cluster.Cluster):
            self._clustersByOffset[child.offsetInBody] = child
            self._clustersByTimestamp[child.timestamp] = child

        return child

    def writeChildElement(self, child):
        offset = super().writeChildElement(child)

        if isinstance(child, matroska.cluster.Cluster):
            self._clustersByOffset[offset] = child
            self._clustersByTimestamp[child.timestamp] = child

        return offset

    def deleteChildElement(self, offset):
        offset = super().deleteChildElement(offset)

        if offset in self.clustersByOffset:
            cluster = self._clustersByOffset.pop(offset)
            del self._clustersByTimestamp[cluster.timestamp]

        return offset

    def iterClusters(self, start_pts=0, trackNumber=None):
        cuePoint = self.findCue(start_pts, trackNumber)
        if cuePoint is not None:
            for cueTrackPosition in cuePoint.cueTrackPositionsList:
                if trackNumber is None or cueTrackPosition.cueTrack == trackNumber:
                    break

            offset = cueTrackPosition.cueClusterPosition

        else:
            offset = 0

        cutoff = 10**9*start_pts/self.info.timestampScale - 32768

        while offset < self._contentssize:
            with self.lock:
                self.seek(offset)
                cluster = self.readCluster()
                offset = self.tell()

            if cluster is not None:
                if cluster.timestamp < cutoff:
                    continue

                yield cluster

    def iterPackets(self, start_pts=0, trackNumber=None):
        I = self.iterClusters(start_pts, trackNumber)

        for cluster in I:
            J = cluster.iterPackets(trackNumber=trackNumber)

            for packet in J:
                if packet.pts >= 10**9*start_pts:
                    break

            else:
                continue

            break

        if packet is not None:
            yield packet

        for packet in J:
            yield packet

        for cluster in I:
            J = cluster.iterPackets(trackNumber=trackNumber)

            for packet in J:
                yield packet

    def writeTopLevel(self, element):
        if element in self.seekHead:
            self.deleteChildElement(self.seekHead[element])

        self.seekHead[element] = self.writeChildElement(element)

    def writeCluster(self):
        clusterOffset = self.tell()

        with self.lock:
            self.seek(192)
            self.writeTopLevel(self.info.copy())
            self.seek(clusterOffset)

            self.writeChildElement(self._currentCluster)
            self.flush()

        inClusterOffset = 0

        for item in self._currentCluster.iterchildren():
            if item in self._blocksToIndex:
                cueTrackPositions = matroska.cues.CueTrackPositions(cueClusterPosition=clusterOffset,
                                                                    cueRelativePosition=inClusterOffset, cueTrack=item.trackNumber)

                cuePoint = matroska.cues.CuePoint(cueTime=item.pts, cueTrackPositionsList=[cueTrackPositions])
                self.cues.cuePoints.append(cuePoint)

            inClusterOffset += item.size()

        self._currentCluster = None
        self._currentBlocks.clear()
        self._blocksToIndex.clear()

    def mux(self, packet):
        trackEntry = self.tracks.tracksByTrackNumber[packet.trackNumber]
        timestampScale = self.info.timestampScale
        isVideoKeyframe = trackEntry.video is not None and packet.keyframe
        isSubtitle = trackEntry.trackType == 17
        nonemptyCluster = self._currentCluster is not None and len(self._currentCluster.blocks)
        ptsOverflow = nonemptyCluster and abs(int(packet.pts/timestampScale - \
                                              self._currentCluster.timestamp)) >= 2**15

        newClusterNeeded = nonemptyCluster and (isVideoKeyframe or ptsOverflow)

        if self._packetsMuxed == 0:
            self.seek(128)
            self.writeTopLevel(self.info.copy())
            self.seek(128, 1)
            self.writeTopLevel(self.tracks)

            if len(self.chapters.editionEntries):
                self.writeTopLevel(self.chapters)

            elif not self.chapters.readonly:
                self.chapters.readonly = True

            if len(self.attachments.attachedFiles):
                self.writeTopLevel(self.attachments)

            elif not self.attachments.readonly:
                self.attachments.readonly = True

            self.flush()

            self._trackPackets = {track.trackNumber: 0 for track in self.tracks.trackEntries}
            self._trackBytes = {track.trackNumber: 0 for track in self.tracks.trackEntries}
            self._trackDurations = {track.trackNumber: 0 for track in self.tracks.trackEntries}

            self._currentCluster = matroska.cluster.Cluster(timestamp=int(packet.pts/timestampScale),
                                                            blocks=[], parent=self)

        if newClusterNeeded:
            self.writeCluster()
            self._currentCluster = matroska.cluster.Cluster(timestamp=int(packet.pts/timestampScale),
                                                            blocks=[], parent=self)

        packet.compression = trackEntry.compression

        localpts = int(packet.pts/timestampScale - self._currentCluster.timestamp)

        isDefaultDuration = packet.duration is None or (trackEntry.defaultDuration is not None and abs(trackEntry.defaultDuration - packet.duration) <= 2)

        maxInLace = trackEntry.maxInLace if trackEntry.maxInLace is not None else 8

        if not isDefaultDuration:
            """Use BlockGroup/Block"""
            block = matroska.blocks.Block(trackNumber=packet.trackNumber, localpts=localpts,
                                                packets=[packet], keyFrame=packet.keyframe, lacing=0)

            blockgroup = matroska.blocks.BlockGroup(block=block,
                                                    blockDuration=int(packet.duration/timestampScale), parent=self._currentCluster)

            self._currentCluster.blocks.append(blockgroup)
            if trackEntry in self._currentBlocks:
                del self._currentBlocks[trackEntry]

            if isVideoKeyframe or isSubtitle:
                self._blocksToIndex.add(blockgroup)

        elif not trackEntry.flagLacing:
            block = matroska.blocks.SimpleBlock(trackNumber=packet.trackNumber, localpts=localpts,
                                                packets=[packet], keyFrame=packet.keyframe, lacing=0,
                                                parent=self._currentCluster)

            self._currentCluster.blocks.append(block)

            if isVideoKeyframe or isSubtitle:
                self._blocksToIndex.add(block)

        elif trackEntry in self._currentBlocks and len(self._currentBlocks[trackEntry].packets) < maxInLace:
            block = self._currentBlocks[trackEntry]

            if block.packets[-1].size != packet.size:
                block.lacing = 0b11

            block.packets.append(packet)
            packet.parent = block

        else:
            block = matroska.blocks.SimpleBlock(trackNumber=packet.trackNumber,
                                                localpts=localpts, packets=[packet],
                                                keyFrame=packet.keyframe, lacing=0b10, parent=self._currentCluster)

            self._currentCluster.blocks.append(block)
            self._currentBlocks[trackEntry] = block

            if isVideoKeyframe or isSubtitle:
                self._blocksToIndex.add(blockgroup)

        self._packetsMuxed += 1
        self._trackPackets[trackEntry.trackNumber] += 1
        self._trackBytes[trackEntry.trackNumber] += packet.size

        if packet.pts is not None and packet.duration is not None:
            currentDuration = self.info.duration
            currentTrackDuration = self._trackDurations.get(trackEntry.trackNumber, 0)

            self._trackDurations[trackEntry.trackNumber] = max(currentTrackDuration, float(packet.pts + packet.duration)/10**9)

            if currentDuration is not None:
                self.info.duration = max(currentDuration, float(packet.pts + packet.duration)/timestampScale)

            else:
                self.info.duration = float(packet.pts + packet.duration)/timestampScale

        elif packet.pts is not None:
            currentTrackDuration = self._trackDurations.get(trackEntry.trackNumber, 0)
            self._trackDurations[trackEntry.trackNumber] = max(currentTrackDuration, float(packet.pts + packet.duration)/10**9)

    def makeStatsTags(self):
        for track in self.tracks.trackEntries:
            size = self._trackBytes.get(track.trackNumber, 0)
            duration = self._trackDurations.get(track.trackNumber, 0)
            n = self._trackPackets.get(track.trackNumber, 0)

            simpleTags = []
            if duration:
                bps = int(8*size/duration+0.5)
                simpleTags.append(matroska.tags.SimpleTag(tagLanguage="eng",
                                                        tagName="BPS", tagString=f"{bps:d}"))

            m, s = divmod(duration, 60)
            m = int(m)
            s = float(s)
            h, m = divmod(m, 60)
            simpleTags.append(matroska.tags.SimpleTag(tagLanguage="eng",
                                                      tagName="DURATION", tagString=f"{h:d}:{m:02d}:{s:012.9f}"))
            simpleTags.append(matroska.tags.SimpleTag(tagLanguage="eng",
                                                      tagName="NUMBER_OF_FRAMES", tagString=f"{n}"))
            simpleTags.append(matroska.tags.SimpleTag(tagLanguage="eng",
                                                      tagName="NUMBER_OF_BYTES", tagString=f"{size}"))
            simpleTags.append(matroska.tags.SimpleTag(tagLanguage="eng",
                                                      tagName="_STATISTICS_WRITING_APP", tagString=f"python {sys.version}"))
            simpleTags.append(matroska.tags.SimpleTag(tagLanguage="eng",
                                                      tagName="_STATISTICS_TAGS", tagString="BPS DURATION NUMBER_OF_BYTES NUMBER_OF_FRAMES"))
            targets = matroska.tags.Targets(tagTrackUIDs=[track.trackUID], targetType="MOVIE", targetTypeValue=50)
            tag = matroska.tags.Tag(simpleTags=simpleTags, targets=targets)
            self.tags.tagList.append(tag)

    def close(self):
        if self._file.writable():
            if self._currentCluster is not None:
                self.writeCluster()

            self.writeTopLevel(self.cues)
            self.makeStatsTags()
            self.writeTopLevel(self.tags)

            segmentSize = self.tell()
            self.seek(0)
            self.writeChildElement(self.seekHead)

        super().close()

    @property
    def packetsMuxed(self):
        return self._packetsMuxed

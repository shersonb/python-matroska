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

    def addVideoTrack(self, pixelWidth, pixelHeight, codecID, name=None, language=None,
                      defaultDuration=None, codecPrivate=None, flagDefault=None, flagForced=None):
        if self.segment.packetsMuxed:
            raise MatroskaError("Tracks must be added before any clusters are written.")

        trackNumber = len(self.segment.tracks.trackEntries) + 1
        existingUIDs = {track.trackUID for track in self.segment.tracks.trackEntries}

        while True:
            trackUID = random.randint(1, 2**64-1)
            if trackUID not in existingUIDs:
                break

        video = matroska.tracks.Video(pixelWidth=pixelWidth, pixelHeight=pixelHeight)
        trackEntry = matroska.tracks.TrackEntry(trackNumber=trackNumber, trackType=1, defaultDuration=defaultDuration,
                                                name=name, language=language, video=video, codecID=codecID, codecPrivate=codecPrivate,
                                                flagForced=flagForced, flagDefault=flagDefault, trackUID=trackUID)
        self.segment.tracks.trackEntries.append(trackEntry)
        return trackEntry
        
    def addAudioTrack(self, samplingFrequency, channels, codecID, name=None, language=None, bitDepth=None,
                       defaultDuration=None, codecPrivate=None, flagDefault=None, flagForced=None, flagLacing=True):

        if self.segment.packetsMuxed:
            raise MatroskaError("Tracks must be added before any clusters are written.")

        trackNumber = len(self.segment.tracks.trackEntries) + 1
        existingUIDs = {track.trackUID for track in self.segment.tracks.trackEntries}

        while True:
            trackUID = random.randint(1, 2**64-1)
            if trackUID not in existingUIDs:
                break

        audio = matroska.tracks.Audio(samplingFrequency=samplingFrequency, channels=channels, bitDepth=bitDepth)
        trackEntry = matroska.tracks.TrackEntry(trackNumber=trackNumber, trackType=2, defaultDuration=defaultDuration,
                                                name=name, language=language, audio=audio, codecID=codecID, codecPrivate=codecPrivate,
                                                flagForced=flagForced, flagDefault=flagDefault, flagLacing=flagLacing, trackUID=trackUID)
        self.segment.tracks.trackEntries.append(trackEntry)
        return trackEntry

    def addSubtitleTrack(self, codecID, name=None, language=None, 
                       defaultDuration=None, codecPrivate=None, flagDefault=None, flagForced=None, compression=0):
        if self.segment.packetsMuxed:
            raise MatroskaError("Tracks must be added before any clusters are written.")
        trackNumber = len(self.segment.tracks.trackEntries) + 1
        existingUIDs = {track.trackUID for track in self.segment.tracks.trackEntries}
        while True:
            trackUID = random.randint(1, 2**64-1)
            if trackUID not in existingUIDs:
                break
        trackEntry = matroska.tracks.TrackEntry(trackNumber=trackNumber, trackType=17, defaultDuration=defaultDuration,
                                                name=name, language=language, codecID=codecID, codecPrivate=codecPrivate,
                                                flagForced=flagForced, flagDefault=flagDefault, trackUID=trackUID)

        if compression is not None:
            trackEntry.contentEncodings = []
            contentCompression = matroska.tracks.ContentCompression(contentCompAlgo=compression)
            contentEncoding = matroska.tracks.ContentEncoding(contentCompression=contentCompression)
            trackEntry.contentEncodings.items.append(contentEncoding)

        self.segment.tracks.trackEntries.append(trackEntry)
        return trackEntry

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

from ebml.base import EBMLInteger, EBMLData, EBMLString, EBMLMasterElement, EBMLFloat, EBMLList, EBMLProperty
#from ebml.util import EBMLList, EBMLProperty, EBMLProperty
#from ebml.util import ebmlproperty as ep

class PrimaryRChromaticityX(EBMLFloat):
    ebmlID = b"\x55\xd1"

class PrimaryRChromaticityY(EBMLFloat):
    ebmlID = b"\x55\xd2"

class PrimaryGChromaticityX(EBMLFloat):
    ebmlID = b"\x55\xd3"

class PrimaryGChromaticityY(EBMLFloat):
    ebmlID = b"\x55\xd4"

class PrimaryBChromaticityX(EBMLFloat):
    ebmlID = b"\x55\xd5"

class PrimaryBChromaticityY(EBMLFloat):
    ebmlID = b"\x55\xd6"

class WhitePointChromaticityX(EBMLFloat):
    ebmlID = b"\x55\xd7"

class WhitePointChromaticityY(EBMLFloat):
    ebmlID = b"\x55\xd8"

class LuminanceMax(EBMLFloat):
    ebmlID = b"\x55\xd9"

class LuminanceMin(EBMLFloat):
    ebmlID = b"\x55\xda"

class MasteringMetadata(EBMLMasterElement):
    ebmlID = b"\x55\xd0"
    __ebmlchildren__ = (
            EBMLProperty("primaryRChromaticityX", PrimaryRChromaticityX, True),
            EBMLProperty("primaryRChromaticityY", PrimaryRChromaticityY, True),
            EBMLProperty("primaryGChromaticityX", PrimaryGChromaticityX, True),
            EBMLProperty("primaryGChromaticityY", PrimaryGChromaticityY, True),
            EBMLProperty("primaryBChromaticityX", PrimaryBChromaticityX, True),
            EBMLProperty("primaryBChromaticityY", PrimaryBChromaticityY, True),
            EBMLProperty("whitePointChromaticityX", WhitePointChromaticityX, True),
            EBMLProperty("whitePointChromaticityY", WhitePointChromaticityY, True),
            EBMLProperty("luminanceMax", LuminanceMax, True),
            EBMLProperty("luminanceMin", LuminanceMin, True),
        )

class MatrixCoefficients(EBMLInteger):
    ebmlID = b"\x55\xb1"

class BitsPerChannel(EBMLInteger):
    ebmlID = b"\x55\xb2"

class ChromaSubsamplingHorz(EBMLInteger):
    ebmlID = b"\x55\xb3"

class ChromaSubsamplingVert(EBMLInteger):
    ebmlID = b"\x55\xb4"

class CbSubsamplingHorz(EBMLInteger):
    ebmlID = b"\x55\xb5"

class CbSubsamplingVert(EBMLInteger):
    ebmlID = b"\x55\xb6"

class ChromaSitingHorz(EBMLInteger):
    ebmlID = b"\x55\xb7"

class ChromaSitingVert(EBMLInteger):
    ebmlID = b"\x55\xb8"

class Range(EBMLInteger):
    ebmlID = b"\x55\xb9"

class TransferCharacteristics(EBMLInteger):
    ebmlID = b"\x55\xba"

class Primaries(EBMLInteger):
    ebmlID = b"\x55\xbb"

class MaxCLL(EBMLInteger):
    ebmlID = b"\x55\xbc"

class MaxFALL(EBMLInteger):
    ebmlID = b"\x55\xbd"

class Colour(EBMLMasterElement):
    ebmlID = b"\x55\xb0"
    __ebmlchildren__ = (
            EBMLProperty("matrixCoefficients", MatrixCoefficients, True),
            EBMLProperty("bitsPerChannel", BitsPerChannel, True),
            EBMLProperty("chromaSubsamplingHorz", ChromaSubsamplingHorz, True),
            EBMLProperty("chromaSubsamplingVert", ChromaSubsamplingVert, True),
            EBMLProperty("cbSubsamplingHorz", CbSubsamplingHorz, True),
            EBMLProperty("cbSubsamplingVert", CbSubsamplingVert, True),
            EBMLProperty("chromaSitingHorz", ChromaSitingHorz, True),
            EBMLProperty("chromaSitingVert", ChromaSitingVert, True),
            EBMLProperty("range", Range, True),
            EBMLProperty("transferCharacteristics", TransferCharacteristics, True),
            EBMLProperty("primaries", Primaries, True),
            EBMLProperty("maxCLL", MaxCLL, True),
            EBMLProperty("maxFALL", MaxFALL, True),
            EBMLProperty("masteringMetadata", MasteringMetadata, True),
        )

class ProjectionType(EBMLInteger):
    ebmlID = b"\x76\x71"

class ProjectionPrivate(EBMLData):
    ebmlID = b"\x76\x72"

class ProjectionPoseYaw(EBMLFloat):
    ebmlID = b"\x76\x73"

class ProjectionPosePitch(EBMLFloat):
    ebmlID = b"\x76\x74"

class ProjectionPoseRoll(EBMLInteger):
    ebmlID = b"\x76\x75"

class Projection(EBMLMasterElement):
    ebmlID = b"\x76\x70"
    __ebmlchildren__ = (
            EBMLProperty("projectionType", ProjectionType),
            EBMLProperty("projectionPrivate", ProjectionPrivate, True),
            EBMLProperty("projectionPoseYaw", ProjectionPoseYaw),
            EBMLProperty("projectionPosePitch", ProjectionPosePitch),
            EBMLProperty("projectionPoseRoll", ProjectionPoseRoll)
        )

class FlagInterlaced(EBMLInteger):
    ebmlID = b"\x9a"

class FieldOrder(EBMLInteger):
    ebmlID = b"\x9d"

class StereoMode(EBMLInteger):
    ebmlID = b"\x53\xb8"

class AlphaMode(EBMLInteger):
    ebmlID = b"\x53\xc0"

class PixelHeight(EBMLInteger):
    ebmlID = b"\xba"

class PixelWidth(EBMLInteger):
    ebmlID = b"\xb0"

class PixelCropBottom(EBMLInteger):
    ebmlID = b"\x54\xaa"

class PixelCropTop(EBMLInteger):
    ebmlID = b"\x54\xbb"

class PixelCropLeft(EBMLInteger):
    ebmlID = b"\x54\xcc"

class PixelCropRight(EBMLInteger):
    ebmlID = b"\x54\xdd"

class DisplayWidth(EBMLInteger):
    ebmlID = b"\x54\xb0"

class DisplayHeight(EBMLInteger):
    ebmlID = b"\x54\xba"

class DisplayUnit(EBMLInteger):
    ebmlID = b"\x54\xb2"

class AspectRatioType(EBMLInteger):
    ebmlID = b"\x54\xb3"

class ColourSpace(EBMLData):
    ebmlID = b"\x2e\xb5\x24"

class Video(EBMLMasterElement):
    ebmlID = b"\xe0"
    __ebmlchildren__ = (
            EBMLProperty("flagInterlaced", FlagInterlaced, True),
            EBMLProperty("fieldOrder", FieldOrder, True),
            EBMLProperty("stereoMode", StereoMode, True),
            EBMLProperty("alphaMode", AlphaMode, True),
            EBMLProperty("pixelWidth", PixelWidth),
            EBMLProperty("pixelHeight", PixelHeight),
            EBMLProperty("pixelCropBottom", PixelCropBottom, True),
            EBMLProperty("pixelCropTop", PixelCropTop, True),
            EBMLProperty("pixelCropLeft", PixelCropLeft, True),
            EBMLProperty("pixelCropRight", PixelCropRight, True),
            EBMLProperty("displayWidth", DisplayWidth, True),
            EBMLProperty("displayHeight", DisplayHeight, True),
            EBMLProperty("displayUnit", DisplayUnit, True),
            EBMLProperty("aspectRatioType", AspectRatioType, True),
            EBMLProperty("colourSpace", ColourSpace, True),
            EBMLProperty("colour", Colour, optional=True),
            EBMLProperty("projection", Projection, optional=True),
        )

class SamplingFrequency(EBMLFloat):
    ebmlID = b"\xb5"

class OutputSamplingFrequency(EBMLFloat):
    ebmlID = b"78\xb5"

class Channels(EBMLInteger):
    ebmlID = b"\x9f"

class BitDepth(EBMLInteger):
    ebmlID = b"\x62\x64"

class Audio(EBMLMasterElement):
    ebmlID = b"\xe1"
    __ebmlchildren__ = (
            EBMLProperty("samplingFrequency", SamplingFrequency),
            EBMLProperty("outputSamplingFrequency", OutputSamplingFrequency, True),
            EBMLProperty("channels", Channels),
            EBMLProperty("bitDepth", BitDepth, True),
        )

class TrackPlaneUID(EBMLInteger):
    ebmlID = b"\xe5"

class TrackPlaneType(EBMLInteger):
    ebmlID = b"\xe6"

class TrackPlane(EBMLMasterElement):
    ebmlID = b"\xe4"
    __ebmlchildren__ = (
            EBMLProperty("trackPlaneUID", TrackPlaneUID),
            EBMLProperty("trackPlaneType", TrackPlaneType),
        )

class TrackPlanes(EBMLList):
    itemclass = TrackPlane

class TrackCombinePlanes(EBMLMasterElement):
    ebmlID = b"\xe3"
    __ebmlchildren__ = (
            EBMLProperty("trackPlanes", TrackPlanes),
        )

class TrackJoinUID(EBMLInteger):
    ebmlID = b"\xed"

class TrackJoinUIDs(EBMLList):
    itemclass = TrackJoinUID
    attrname = "value"

class TrackJoinBlocks(EBMLMasterElement):
    ebmlID = b"\xe9"
    __ebmlchildren__ = (
            EBMLProperty("trackJoinUIDs", TrackJoinUIDs),
        )

class TrackOperation(EBMLMasterElement):
    ebmlID = b"\xe2"
    __ebmlchildren__ = (
            EBMLProperty("trackCombinePlanes", TrackCombinePlanes, optional=True),
            EBMLProperty("trackJoinBlocks", TrackJoinBlocks, optional=True),
        )

class AESSettingsCipherMode(EBMLInteger):
    ebmlID = b"\x47\xe8"

class ContentEncAESSettings(EBMLMasterElement):
    ebmlID = b"\x47\xe7"
    __ebmlchildren__ = (
            EBMLProperty("aesSettingsCipherMode", AESSettingsCipherMode),
        )

class ContentEncAlgo(EBMLInteger):
    ebmlID = b"\x47\xe1"

class ContentEncKeyID(EBMLData):
    ebmlID = b"\x47\xe2"

class ContentSignature(EBMLData):
    ebmlID = b"\x47\xe3"

class ContentSigKeyID(EBMLData):
    ebmlID = b"\x47\xe4"

class ContentSigAlgo(EBMLInteger):
    ebmlID = b"\x47\xe5"

class ContentSigHashAlgo(EBMLInteger):
    ebmlID = b"\x47\xe6"

class ContentEncryption(EBMLMasterElement):
    ebmlID = b"\x50\x35"
    __ebmlchildren__ = (
            EBMLProperty("contentEncAlgo", ContentEncAlgo, True),
            EBMLProperty("contentEncKeyID", ContentEncKeyID, True),
            EBMLProperty("contentEncAESSettings", ContentEncAESSettings, optional=True),
            EBMLProperty("contentSignature", ContentSignature, True),
            EBMLProperty("contentSigKeyID", ContentSigKeyID, True),
            EBMLProperty("contentSigAlgo", ContentSigAlgo, True),
            EBMLProperty("contentSigHashAlgo", ContentSigHashAlgo, True),
        )

class ContentCompAlgo(EBMLInteger):
    ebmlID = b"\x42\x54"
    data = EBMLProperty("data", int)
    __ebmlproperties__ = (data,)

    @data.sethook
    def data(self, value):
        if isinstance(value, int) and value not in (0, 1, 2, 3):
            raise ValueError("Invalid value for ContentCompAlgo.")

        return value

class ContentCompSettings(EBMLData):
    ebmlID = b"\x42\x55"

class ContentCompression(EBMLMasterElement):
    ebmlID = b"\x50\x34"
    __ebmlchildren__ = (
            EBMLProperty("contentCompAlgo", ContentCompAlgo, True),
            EBMLProperty("contentCompSettings", ContentCompSettings, True)
        )

class ContentEncodingOrder(EBMLInteger):
    ebmlID = b"\x50\x31"

class ContentEncodingScope(EBMLInteger):
    ebmlID = b"\x50\x32"

class ContentEncodingType(EBMLInteger):
    ebmlID = b"\x50\x33"

class ContentEncoding(EBMLMasterElement):
    ebmlID = b"\x62\x40"
    __ebmlchildren__ = (
            EBMLProperty("contentEncodingOrder", ContentEncodingOrder, True),
            EBMLProperty("contentEncodingScope", ContentEncodingScope, True),
            EBMLProperty("contentEncodingType", ContentEncodingType, True),
            EBMLProperty("contentCompression", ContentCompression, optional=True),
            EBMLProperty("contentEncryption", ContentEncryption, optional=True),
        )

class ContentEncodingList(EBMLList):
    itemclass = ContentEncoding

class ContentEncodings(EBMLMasterElement):
    ebmlID = b"\x6d\x80"
    __ebmlchildren__ = (
            EBMLProperty("items", ContentEncodingList),
        )

class TrackTranslateTrackID(EBMLData):
    ebmlID = b"\x66\xa5"

class TrackTranslateCodec(EBMLInteger):
    ebmlID = b"\x66\xbf"

class TrackTranslateEditionUID(EBMLInteger):
    ebmlID = b"\x66\xfc"

class TrackTranslateEditionUIDs(EBMLList):
    itemclass = TrackTranslateEditionUID
    attrname = "value"

class TrackTranslate(EBMLMasterElement):
    ebmlID = b"\x66\x24"
    __ebmlchildren__ = (
            EBMLProperty("trackTranslateEditionUIDs", TrackTranslateEditionUIDs, optional=True),
            EBMLProperty("trackTranslateCodec", TrackTranslateCodec),
            EBMLProperty("trackTranslateTrackID", TrackTranslateTrackID),
        )

class TrackNumber(EBMLInteger):
    ebmlID = b"\xd7"

class TrackUID(EBMLInteger):
    ebmlID = b"\x73\xc5"

class TrackType(EBMLInteger):
    ebmlID = b"\x83"

class FlagEnabled(EBMLInteger):
    ebmlID = b"\xb9"

class FlagDefault(EBMLInteger):
    ebmlID = b"\x88"

class FlagForced(EBMLInteger):
    ebmlID = b"\x55\xaa"

class FlagLacing(EBMLInteger):
    ebmlID = b"\x9c"

class MinCache(EBMLInteger):
    ebmlID = b"\x6d\xe7"

class MaxCache(EBMLInteger):
    ebmlID = b"\x6d\xf8"

class DefaultDuration(EBMLInteger):
    ebmlID = b"\x23\xe3\x83"

class DefaultDecodedFieldDuration(EBMLInteger):
    ebmlID = b"\x23\x43\x7a"

class MaxBlockAdditionID(EBMLInteger):
    ebmlID = b"\x55\xee"

class Name(EBMLString):
    ebmlID = b"\x53\x6e"

class Language(EBMLString):
    ebmlID = b"\x22\xb5\x9c"

class LanguageIETF(EBMLString):
    ebmlID = b"\x22\xb5\x9d"

class CodecID(EBMLString):
    ebmlID = b"\x86"

class CodecPrivate(EBMLData):
    ebmlID = b"\x63\xa2"

class CodecName(EBMLString):
    ebmlID = b"\x25\x86\x88"

class CodecDecodeAll(EBMLInteger):
    ebmlID = b"\xaa"

class TrackOverlay(EBMLInteger):
    ebmlID = b"\x6f\xab"

class TrackOverlays(EBMLList):
    itemclass = TrackOverlay
    #attrname = "value"

CodecDelay = EBMLInteger.makesubclass("CodecOverlay", prefix=b"\x56\xaa")
class SeekPreRoll(EBMLInteger):
    ebmlID = b"\x56\xbb"

class TrackTranslates(EBMLList):
    itemclass = TrackTranslate

class TrackEntry(EBMLMasterElement):
    ebmlID = b"\xae"
    __ebmlchildren__ = (
            EBMLProperty("trackNumber", TrackNumber),
            EBMLProperty("trackUID", TrackUID),
            EBMLProperty("trackType", TrackType),
            EBMLProperty("flagEnabled", FlagEnabled, True),
            EBMLProperty("flagDefault", FlagDefault, True),
            EBMLProperty("flagForced", FlagForced, True),
            EBMLProperty("flagLacing", FlagLacing, True),
            EBMLProperty("minCache", MinCache, True),
            EBMLProperty("maxCache", MaxCache, True),
            EBMLProperty("defaultDuration", DefaultDuration, True),
            EBMLProperty("defaultDecodedFieldDuration", DefaultDecodedFieldDuration, True),
            EBMLProperty("maxBlockAdditionID", MaxBlockAdditionID, True),
            EBMLProperty("name", Name, True),
            EBMLProperty("language", Language, True),
            EBMLProperty("languageIETF", LanguageIETF, True),
            EBMLProperty("codecID", CodecID),
            EBMLProperty("codecPrivate", CodecPrivate, True),
            EBMLProperty("codecName", CodecName, True),
            EBMLProperty("codecDecodeAll", CodecDecodeAll, True),
            EBMLProperty("trackOverlays", TrackOverlays, optional=True),
            EBMLProperty("codecDelay", CodecDelay, True),
            EBMLProperty("seekPreRoll", SeekPreRoll, True),
            EBMLProperty("trackTranslates", TrackTranslates, optional=True),
            EBMLProperty("video", Video, optional=True),
            EBMLProperty("audio", Audio, optional=True),
            EBMLProperty("trackOperation", TrackOperation, optional=True),
            EBMLProperty("contentEncodings", ContentEncodings, optional=True)
        )
    __ebmlproperties__ = (EBMLProperty("maxInLace", int, optional=True),)

    @property
    def compression(self):
        if self.contentEncodings is None:
            return

        for entry in self.contentEncodings.items:
            if entry.contentCompression is None:
                continue

            if entry.contentCompression.contentCompAlgo is not None:
                return entry.contentCompression.contentCompAlgo

            return 0

    @compression.setter
    def compression(self, value):
        if value is None:
            if self.contentEncodings is None:
                return

            for entry in list.copy(self.contentEncodings.items):
                if entry.contentCompression is not None:
                    self.contentEncodings.items.remove(entry)

        else:
            if self.contentEncodings is None:
                self.contentEncodings = ContentEncodings(items=[])

            for entry in self.contentEncodings.items:
                if entry.contentCompression is not None:
                    entry.contentCompression.contentCompAlgo = value
                    return

            contentEncoding = ContentEncoding
            self.contentEncodings.items.append(ContentEncoding(contentCompression=value))

class TrackEntries(EBMLList):
    itemclass = TrackEntry

class Tracks(EBMLMasterElement):
    ebmlID = b"\x16\x54\xae\x6b"
    trackEntries = EBMLProperty("trackEntries", TrackEntries)
    __ebmlchildren__ = (trackEntries,)

    @property
    def append(self):
        return self.trackEntries.append

    @property
    def insert(self):
        return self.trackEntries.insert

    @property
    def remove(self):
        return self.trackEntries.remove

    @property
    def extend(self):
        return self.trackEntries.extend

    @property
    def __iter__(self):
        return self.trackEntries.__iter__

    @property
    def __getitem__(self):
        return self.trackEntries.__getitem__

    @property
    def byTrackNumber(self):
        return {track.trackNumber: track for track in self.trackEntries}

    @property
    def video(self):
        return tuple(track for track in self.trackEntries if track.trackType == 1)

    @property
    def audio(self):
        return tuple(track for track in self.trackEntries if track.trackType == 2)

    @property
    def subtitles(self):
        return tuple(track for track in self.trackEntries if track.trackType == 17)

    def clone(self, track):
        trackNumber = 1
        tracksByTrackNumber = self.byTrackNumber

        while trackNumber in tracksByTrackNumber:
            trackNumber += 1

        track = track.copy(parent=self)
        track.trackNumber = trackNumber
        self.append(track)
        return track

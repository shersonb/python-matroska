from ebml.base import EBMLInteger, EBMLData, EBMLMasterElement, EBMLList, EBMLProperty
from ebml.util import formatBytes

__all__ = ["SeekID", "SeekPosition", "Seek", "SeekHead"]

class SeekID(EBMLData):
    ebmlID = b"\x53\xab"

class SeekPosition(EBMLInteger):
    ebmlID = b"\x53\xac"

class Seek(EBMLMasterElement):
    ebmlID = b"\x4d\xbb"
    __ebmlchildren__ = (
            EBMLProperty("seekID", SeekID),
            EBMLProperty("seekPosition", SeekPosition)
        )

class Seeks(EBMLList):
    itemclass = Seek

class SeekHead(EBMLMasterElement):
    ebmlID = b"\x11\x4d\x9b\x74"
    __ebmlchildren__ = (EBMLProperty("seeks", Seeks),)

    def __getitem__(self, cls):
        for seek in self.seeks:
            if seek.seekID == cls.ebmlID:
                return seek.seekPosition

        raise KeyError(f"{formatBytes(cls.ebmlID)}")

    def __setitem__(self, cls, value):
        for seek in self.seeks:
            if seek.seekID == cls.ebmlID:
                seek.seekPosition = value
                break
        else:
            self.seeks.append(Seek(seekID=cls.ebmlID, seekPosition=value))

    def __delitem__(self, cls):
        for seek in self.seeks:
            if seek.seekID == cls.ebmlID:
                self.seeks.remove(seek)
                return

        raise KeyError(f"{formatBytes(cls.ebmlID)}")

    def __contains__(self, cls):
        for seek in self.seeks:
            if seek.seekID == cls.ebmlID:
                return True

        return False

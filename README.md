#  python-matroska

Matroska muxer/demuxer for Python.

## Usage

```python
import matroska

# Opens an MKV file in read mode.
f = matroska.MatroskaFile("movie.mkv", "r")
for packet in f.demux(trackNumber=1):
    print(packet) # prints all packets in the first track

# Opens an MKV file in write mode
g = matroska.MatroskaFile("movie2.mkv", "w")

# Adds a track to "movie2.mkv" using the
# first track in "movie.mkv" as a template.
newtrack = g.tracks.clone(f.tracks.byTrackNumber[1])

# Sets the segment title of "movie2.mkv"
g.title = f.title

for packet in f.demux(trackNumber=1):
    packet = packet.copy()
    packet.trackNumber = newtrack.trackNumber
    g.mux(packet) # remuxes track

f.close()
g.close()
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

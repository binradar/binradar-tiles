"""Unpacks a PMTiles archive into a static {z}/{x}/{y}.pbf directory.

GitHub Pages ignores HTTP Range requests, so it cannot serve a .pmtiles
archive to a browser; a plain directory of tiles works on any static host.
Pages also never sets Content-Encoding for .pbf files, so every tile is
written decompressed and MapLibre can read it as-is.

Usage: python scripts/unpack.py <archive.pmtiles> <output-dir>
"""

import gzip
import sys
from pathlib import Path

from pmtiles.reader import MmapSource, all_tiles, deserialize_header
from pmtiles.tile import Compression

DECOMPRESS = {
	Compression.NONE: lambda data: data,
	Compression.GZIP: gzip.decompress,
}


def main(archive, out_dir):
	with open(archive, "rb") as f:
		get_bytes = MmapSource(f)
		compression = deserialize_header(get_bytes(0, 127))["tile_compression"]
		if compression not in DECOMPRESS:
			sys.exit(f"unsupported tile compression: {compression.name}")
		decompress = DECOMPRESS[compression]

		count = 0
		for (z, x, y), data in all_tiles(get_bytes):
			path = Path(out_dir, str(z), str(x), f"{y}.pbf")
			path.parent.mkdir(parents=True, exist_ok=True)
			path.write_bytes(decompress(data))
			count += 1

	print(f"unpacked {count} tiles into {out_dir}")


if __name__ == "__main__":
	if len(sys.argv) != 3:
		sys.exit(__doc__)
	main(sys.argv[1], sys.argv[2])

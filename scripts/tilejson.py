"""Writes a TileJSON 3.0.0 document for the unpacked tiles to stdout.

Lets MapLibre, Maputnik and other clients add the layer by a single URL
instead of repeating its tile template, zoom range and fields. Zoom range,
bounds, fields and attribution come from the archive itself. The name is
passed in, because tile-join joins every region's name into the archive's
own name field.

Usage: python scripts/tilejson.py <archive.pmtiles> <tiles-base-url> <name>
"""

import json
import sys

from pmtiles.reader import MmapSource, Reader


def main(archive, tiles_base_url, name):
	with open(archive, "rb") as f:
		reader = Reader(MmapSource(f))
		header = reader.header()
		metadata = reader.metadata()

	tilejson = {
		"tilejson": "3.0.0",
		"name": name,
		"description": metadata.get("description", ""),
		"attribution": metadata.get("attribution", ""),
		"tiles": [f"{tiles_base_url}/{{z}}/{{x}}/{{y}}.pbf"],
		"minzoom": header["min_zoom"],
		"maxzoom": header["max_zoom"],
		"bounds": [
			header["min_lon_e7"] / 1e7,
			header["min_lat_e7"] / 1e7,
			header["max_lon_e7"] / 1e7,
			header["max_lat_e7"] / 1e7,
		],
		"vector_layers": metadata["vector_layers"],
	}
	json.dump(tilejson, sys.stdout, indent="\t", ensure_ascii=False)


if __name__ == "__main__":
	if len(sys.argv) != 4:
		sys.exit(__doc__)
	main(*sys.argv[1:])

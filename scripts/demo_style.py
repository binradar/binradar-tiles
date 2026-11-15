"""Writes a demo MapLibre style to stdout: an OpenFreeMap basemap plus bins.

Meant for a quick look at the tiles, e.g. in Maputnik via
https://maplibre.org/maputnik/?style=<style-url>. The basemap style is
fetched at deploy time, so the demo follows OpenFreeMap's own updates.
The bins are plain circles coloured by `class`; `precision=low` ones
(bin=yes proxies) are drawn half transparent.

Usage: python scripts/demo_style.py <basemap-style-url> <tilejson-url>
"""

import json
import sys
import urllib.request

BINS_LAYER = {
	"id": "bins",
	"type": "circle",
	"source": "bins",
	"source-layer": "bins",
	"paint": {
		"circle-color": [
			"match", ["get", "class"],
			"recycling", "#2b8a3e",
			"waste_disposal", "#e8590c",
			"#1971c2",
		],
		"circle-radius": ["interpolate", ["linear"], ["zoom"], 14, 3, 18, 8],
		"circle-opacity": ["case", ["==", ["get", "precision"], "low"], 0.5, 1],
		"circle-stroke-color": "#ffffff",
		"circle-stroke-width": 1,
	},
}


def main(basemap_style_url, tilejson_url):
	# OpenFreeMap rejects urllib's default User-Agent with a 403.
	request = urllib.request.Request(
		basemap_style_url,
		headers={"User-Agent": "binradar-tiles (https://github.com/binradar/binradar-tiles)"},
	)
	with urllib.request.urlopen(request) as response:
		style = json.load(response)

	style["name"] = "BinRadar demo"
	style["sources"]["bins"] = {"type": "vector", "url": tilejson_url}
	style["layers"].append(BINS_LAYER)
	json.dump(style, sys.stdout, indent="\t", ensure_ascii=False)


if __name__ == "__main__":
	if len(sys.argv) != 3:
		sys.exit(__doc__)
	main(*sys.argv[1:])

# binradar-tiles

A worldwide PMTiles layer of public waste baskets, waste disposal
containers, and recycling points (OSM `amenity=waste_basket`,
`amenity=waste_disposal`, `amenity=recycling`, and `bin=yes` as a lower
precision proxy for a waste basket), built at the single zoom level 14
from Geofabrik OSM extracts via
[TileDistillery](https://github.com/tilelab/tiledistillery), and also
served as static tiles on GitHub Pages.
This repo only configures TileDistillery's reusable GitHub Actions
workflow; apart from unpacking the result for Pages, it does not implement
any of the build mechanics itself.

## Layout

| Path | Purpose |
| --- | --- |
| `tiles/config.json` | tilemaker layer config: one `bins` layer at the single zoom level 14, the same level Mapillary serves its map features at, which clients overzoom, with `include_ids` enabled so every feature also carries its OSM node id as the tile's own feature id. |
| `tiles/process.lua` | tilemaker profile: emits nodes tagged `amenity=waste_basket`, `amenity=waste_disposal`, `amenity=recycling`, or `bin=yes` into `bins`, tagged with `class` (`waste_basket`, `waste_disposal`, or `recycling`) so the types stay distinguishable. `bin=yes` nodes are tagged `class=waste_basket` with `precision=low`, since that tag is a weaker signal than a proper amenity tag. Every feature also carries an `id` attribute plus `name`, `opening_hours` and `operator` when present; `waste` is recorded for the waste classes, and `recycling_type` plus `recycling` (every `recycling:<material>=yes`, joined as `clothes;glass_bottles;paper`) for recycling, all optional. |
| `.github/workflows/build.yml` | Calls TileDistillery's `_pipeline.yml` (Sundays 03:00 UTC + manual), then publishes `bins.pmtiles` as a GitHub Release via its `_publish-release.yml` and deploys the unpacked tiles to GitHub Pages. |
| `scripts/unpack.py` | Unpacks `bins.pmtiles` into a decompressed `{z}/{x}/{y}.pbf` directory for Pages, which gzips responses on the fly and applies Range requests to the compressed bytes, so cannot serve the archive itself. |
| `scripts/tilejson.py` | Writes the TileJSON (`bins.json`) for the Pages tiles, taking zoom range, bounds, fields and attribution from the archive. |
| `scripts/demo_style.py` | Writes a demo MapLibre style (`style.json`): OpenFreeMap's Positron basemap plus the bins as circles coloured by `class`. |

## Using the tiles

Browsers can't read the release asset, since GitHub Releases send no CORS
headers. Point MapLibre at the Pages copy instead, as a vector source by its
TileJSON:

```js
map.addSource("bins", {
  type: "vector",
  url: "https://binradar.github.io/binradar-tiles/bins.json",
});
```

The tiles are only at zoom 14 (`bins/{z}/{x}/{y}.pbf`); MapLibre overzooms
them above that and shows nothing below it. Pages answers tiles without any
bins with a 404.

For a quick look, open the demo style in Maputnik:
<https://maplibre.org/maputnik/?style=https://binradar.github.io/binradar-tiles/style.json#14/52.52/13.405>

## How it builds

See [How the pipeline works](https://github.com/tilelab/tiledistillery/blob/main/docs/explanation/architecture.md)
for the actual mechanics: how Geofabrik leaf extracts are detected, how they
are split into shards of about equal size up front, and how each region's
tiles are merged into one `.pmtiles`. This repo only supplies the tilemaker
config/profile and picks the publish targets. TileDistillery only reads this
repository, so the build job needs no more than `contents: read`; the
`state` branch earlier versions kept here is no longer used. The `pages`
job takes the same `bins-pmtiles` artifact the release is made from.

## Related projects

- **[TileDistillery](https://github.com/tilelab/tiledistillery)** —
  the reusable pipeline this repo calls. Builds PMTiles layers from raw
  Geofabrik OSM extracts with tilemaker.
- **[TileAlchemist](https://github.com/tilelab/tilealchemist)** — a
  sibling of TileDistillery, not used here. It reshapes an *existing*
  PMTiles archive tile by tile via pluggable profiles (e.g. inverting water
  into land) instead of building from raw OSM extracts. Relevant if you want
  a base layer to render these bins on top of; unrelated to how this layer
  is produced.

## License / attribution

Map data built by this pipeline is OpenStreetMap data via Geofabrik,
© OpenStreetMap contributors, available under the
[Open Database License (ODbL)](https://www.openstreetmap.org/copyright).

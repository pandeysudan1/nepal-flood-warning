# Sample Sentinel-2 scenes

These files demonstrate catalogue discovery and preview download for the Imja Lake test region.

- `imja_sentinel2_feb2026_catalog.csv` was generated from the official Copernicus Data Space STAC API.
- `imja_sentinel2_catalog.csv` records the April 2026 scene cited in the monitoring plan.
- The JPEG files are official scene thumbnails returned by the catalogue.

The thumbnails show full Sentinel-2 tiles. They are not cropped lake measurements and must not be used to calculate lake area. Scientific processing should read the source bands, apply quality masks, crop them with a validated lake polygon, and preserve the scene identifier.

Catalogue endpoint: <https://stac.dataspace.copernicus.eu/v1/collections/sentinel-2-l2a>

Copernicus Sentinel data use is governed by the legal notice linked from the collection metadata.


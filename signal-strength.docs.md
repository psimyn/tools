# Signal Strength

Live map of mobile phone reception across Victoria and Melbourne, combining
official coverage polygons and cell-site locations from multiple open
data sources.

## Prompt

> make an app called signal strength, showing a map of Victoria/Melbourne
> and cell phone reception. search for multiple/best data sources and
> combine

## Data sources

The app overlays two classes of data on an OpenStreetMap / CARTO dark
basemap:

1. **ACCC Mobile Infrastructure — Coverage polygons.** Sourced from the
   federal Department of Infrastructure's ArcGIS service at
   `spatial.infrastructure.gov.au`, which republishes the ACCC's annual
   *Audit of Telecommunications Infrastructure Assets* (Infrastructure
   RKR). Every quarter the three national MNOs (Telstra, Optus, TPG /
   Vodafone) submit predicted coverage rasters for 3G / 4G / 5G, both
   outdoor handheld and external-antenna. The app prefers the *outdoor*
   variants since they match normal phone use.

2. **ACMA Mobile Phone Sites.** Points drawn from the ACMA Register of
   Radiocommunications Licences — the authoritative list of licensed
   transmitters in Australia. Useful for spotting why a pocket of no
   reception exists (no tower nearby) or why coverage suddenly improves
   (new tower).

Both services are consumed via ArcGIS REST `MapServer` endpoints using
[esri-leaflet](https://github.com/Esri/esri-leaflet), so there's no
server of our own and no API key.

## Features

- **Technology filter** — toggle between all / 5G / 4G / 3G.
- **Carrier filter** — show or hide Telstra, Optus and TPG independently
  (each carrier renders as a distinct colour).
- **Cell-site toggle** — overlay the ACMA RRL transmitter points.
- **Tap to identify** — clicking anywhere runs an ArcGIS Identify query
  and reports which carriers × techs claim coverage at that spot.
- **Locate me** — drops a pin at your GPS location and runs an identify
  right there, so you can compare "what the carrier promises" with
  "what your phone actually sees".
- **Adjustable overlay opacity** — the polygons are semi-transparent by
  default so the basemap stays readable.

## Implementation notes

- **Dynamic layer discovery.** Layer IDs inside the provider MapServer
  drift between quarterly data refreshes, so rather than hard-coding
  them the app probes a short list of candidate ArcGIS services at
  boot (newest ACCC service first) and classifies each sub-layer by
  matching carrier and technology keywords in the layer name, picking
  the first service that actually yields matches. Combined "Total" /
  "ALL" layers are mapped to the "all tech" bucket so the UI toggle
  can surface them even when per-generation sub-layers are missing.
- **CORS fallback.** Metadata is fetched through `L.esri.request`,
  which falls back to JSONP when the server doesn't send CORS
  headers — plain `fetch()` would silently fail on older public
  ArcGIS deployments.
- **Single identify request per click.** ArcGIS supports identifying
  against multiple sub-layers in one request. The app asks for every
  currently-enabled layer at once and groups the results by carrier ×
  tech, so the popup can say "Telstra: 5G, 4G · Optus: 4G · TPG: no
  signal" after a single round-trip.
- **No build step.** One self-contained HTML file. Leaflet and
  esri-leaflet are loaded from unpkg.
- Carrier colours — Telstra blue, Optus orange, TPG/Vodafone red —
  roughly mirror their brand palettes for quick recognition.

## Caveats

- Coverage polygons are *predictive* — what the carrier says should
  work, not what a real device measures. They're known to be
  optimistic, especially indoors. Treat them as an upper bound.
- The ACMA sites layer includes *all* licensed radiocommunications
  transmitters, not just mobile cell towers, so at very high zoom
  levels you'll see more points than just 3/4/5G sites.
- The app isn't attempting to crowdsource real-world measurements
  (OpenCellID, etc.) because those services require per-user API keys
  that don't belong in a static single-file page.

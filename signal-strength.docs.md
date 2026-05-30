# Signal Strength

Live map of mobile phone reception across Victoria and Melbourne, combining
official coverage polygons, licensed transmitter sites, and government-funded
black-spot towers from three independent open-data sources.

## Prompt

> make an app called signal strength, showing a map of Victoria/Melbourne
> and cell phone reception. search for multiple/best data sources and
> combine

## Data sources

The app overlays three classes of data on an OpenStreetMap / CARTO dark
basemap. All three are public ArcGIS REST services published by the federal
Department of Infrastructure at `spatial.infrastructure.gov.au`, so the app
needs no server of its own and no API keys.

1. **ACCC Mobile Infrastructure — coverage polygons.** Republished from the
   ACCC's annual *Audit of Telecommunications Infrastructure Assets*
   (Infrastructure RKR). Every quarter the three national MNOs (Telstra,
   Optus, TPG / Vodafone) submit predicted coverage rasters for 3G / 4G /
   5G in both *outdoor* and *external-antenna* variants. The app prefers
   outdoor since it matches normal handheld use. The 2025 service also
   surfaces TPG's MOCN coverage on Optus's network as a separate sub-layer
   — these are folded under the TPG carrier toggle.

2. **ACMA Mobile Phone Sites.** Points drawn from the ACMA Register of
   Radiocommunications Licences — the authoritative list of licensed
   transmitters in Australia. Useful for explaining a coverage gap
   ("there's no tower nearby") or a sudden coverage edge ("new site went
   live here").

3. **Mobile Black Spot Program funded base stations.** Government-funded
   towers from rounds 1 through 8 of the MBSP, currently building out
   reception in regional Victoria. Drawn as purple points. Combined with
   the predicted-coverage polygons they answer the question "is patchy
   coverage here going to get better?".

A separate place-search box uses the public **Nominatim** OSM geocoder,
bounded to a Victoria viewbox so a search for "St Kilda" lands in
Melbourne and not in Otago.

All ArcGIS sources are consumed via
[esri-leaflet](https://github.com/Esri/esri-leaflet) dynamic-map layers
plus a single ArcGIS Identify request per click for the popup.

## Features

- **Technology filter** — toggle between all / 5G / 4G / 3G.
- **Carrier filter** — show or hide Telstra, Optus and TPG independently
  (each carrier renders as a distinct colour).
- **Cell-site toggle** — overlay the ACMA RRL transmitter points.
- **Black-spot tower toggle** — overlay MBSP funded base stations.
- **Place search** — type a Victorian town or suburb, jump to it, and
  auto-identify coverage there.
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
- **Debounced, scoped place search.** Nominatim queries are debounced
  to ~280 ms and tagged with a sequence number so a slow response from
  an older keystroke can't overwrite the latest results. The viewbox +
  `bounded=1` + `countrycodes=au` parameters keep matches local.
- **No build step.** One self-contained HTML file. Leaflet and
  esri-leaflet are loaded from unpkg.
- Carrier colours — Telstra blue, Optus orange, TPG/Vodafone red,
  black-spot towers purple — roughly mirror brand palettes for quick
  recognition.

## Caveats

- Coverage polygons are *predictive* — what the carrier says should
  work, not what a real device measures. They're known to be
  optimistic, especially indoors. Treat them as an upper bound.
- The ACMA sites layer includes *all* licensed radiocommunications
  transmitters, not just mobile cell towers, so at very high zoom
  levels you'll see more points than just 3/4/5G sites.
- MBSP locations are *indicative* of where funded towers go. Some are
  already live, others are still under construction — the data set
  doesn't differentiate.
- The app intentionally avoids crowdsourced measurement services
  (OpenCellID, OpenSignal, nPerf etc.) because they require per-user
  API keys that don't belong in a static single-file page.

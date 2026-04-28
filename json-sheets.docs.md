# JSON Sheets

Paste JSON or fetch a URL, get a table you can drop straight into Google
Sheets or Excel. Every nested field becomes its own dot-path column —
`address.city`, `posts.0.title`, etc. — so nothing hides inside a
JSON-stringified cell. The **Copy for Sheets** button puts a TSV on the
clipboard; **Copy & open Sheets** does the same and opens a fresh
`sheets.new` tab so you only need to hit ⌘/Ctrl-V.

## Prompt

> new tool called json sheets
>
> paste a url to fetch an endpoint, or a blob of json text
> gets converted into a table with heading names from keys
> have some options to flatten or nest/dot.name fields. then a copy button to
> copy to clipboard in a format I can paste into a sheet. or if that is
> possible with a sheets url to prefill that'd be super

## How it works

- **Row detection.** If the JSON is an array, that's the rows. If it's an
  object, the tool unwraps common wrappers (`results`, `data`, `items`,
  `rows`, `records`, `values`, `entries`) one or two levels deep, then falls
  back to any top-level array, then to treating the whole object as a single
  row.
- **Flattening.** Nested objects always recurse into dot.path columns
  (`address.city`, `address.country`).
- **Arrays of primitives** are joined with `, ` so they read cleanly in a
  cell (`tags` → `math, cs`).
- **Arrays of objects** expand by index when *expand arrays of objects* is
  on (`posts.0.title`, `posts.1.title`, …) and stay as compact JSON in a
  single cell when it's off — handy if those arrays are long or ragged.
- **Headers** are the union of keys across all rows, in first-seen order.

## Copying & Sheets

- **Copy for Sheets** writes TSV to the clipboard. Embedded tabs/newlines are
  collapsed to spaces so each value lands in exactly one cell on paste.
- **Copy CSV** uses RFC-4180 quoting (commas, quotes and newlines preserved).
- **Copy & open Sheets** copies TSV and opens `https://sheets.new`. Google
  Sheets has no public URL for prefilling arbitrary data into a new sheet, so
  one paste is the closest we can get.

## Notes

- Fetching arbitrary URLs from the browser is subject to CORS — if a server
  doesn't allow cross-origin reads, the fetch fails and you'll need to paste
  the JSON manually.
- The preview is capped at 500 rows for responsiveness; copy always uses the
  full dataset.
- Single-file, no dependencies.

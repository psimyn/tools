# Base64 & friends

A two-pane encoder/decoder. Type into either side and the other updates live —
plain text on the left, encoded on the right. Pick the encoding from the top
bar; relevant options (padding, URL-safe alphabet, hex case, binary spaces)
appear automatically.

## Prompt

> base64 encoder and decoder, with options for other encodings too

## Encodings

- **Base64** (RFC 4648) — toggles for URL-safe alphabet (`-_` instead of `+/`)
  and trailing padding. Decode accepts either alphabet, with or without
  padding, and ignores whitespace.
- **Base32** (RFC 4648) — `A–Z` `2–7`, optional `=` padding.
- **Hex** (Base16) — lowercase or uppercase, with whitespace and a leading
  `0x` ignored on decode.
- **URL** — percent-encoding via `encodeURIComponent` / `decodeURIComponent`,
  with `+` → space on decode for form-style input.
- **HTML** — escapes `& < > " '` on encode; on decode resolves named entities
  (`&amp;`, `&copy;`, …), decimal `&#65;`, and hex `&#x41;`.
- **Binary** — 8 bits per byte, optional spaces between bytes.
- **ASCII85** — Adobe-flavored, with the `<~` `~>` markers stripped on decode.

## Notes

- All encodings round-trip arbitrary UTF-8 (including emoji). Base64, Base32,
  Hex, Binary and ASCII85 operate on raw bytes; URL and HTML work directly on
  the string.
- Decode is forgiving: whitespace is ignored everywhere, padding is optional
  on Base64/Base32, and Base64 accepts both standard and URL-safe alphabets in
  the same input.
- Errors (invalid characters, odd-length hex, mis-padded binary) are shown in
  the status bar and the failing pane is outlined red, instead of silently
  producing junk.
- Single-file, no dependencies.

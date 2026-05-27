# Barcode

Generate a barcode from any text you type or paste, or scan one with your
device camera and read the decoded text back. Two tabs in one page: **Generate**
renders a live barcode you can download as a PNG or print; **Scan** opens the
camera and decodes 1D barcodes and QR codes, showing the result with a copy
button.

## Prompt

> add a barcode generator/scanner. either paste text to print a barcode, or button to trigger camera that scans a barcode and show text

## Notes

- Single self-contained HTML file. Generation uses
  [JsBarcode](https://github.com/lindell/JsBarcode); scanning uses
  [ZXing](https://github.com/zxing-js/library), both loaded from a CDN.
- **Generate**: Code 128 is the default (it encodes arbitrary text); a format
  dropdown also offers Code 39, EAN-13/8, UPC-A, ITF-14, MSI, Codabar and
  Pharmacode. Invalid input for the chosen format surfaces a clear error.
- The barcode is rendered as inline SVG, so it stays crisp at any size. **Print**
  uses a print stylesheet that shows only the barcode; **Download PNG**
  rasterises the SVG to a 3× canvas for a sharp bitmap.
- **Scan**: `ZXing.BrowserMultiFormatReader` reads from the live camera via
  `getUserMedia`, preferring the rear camera (`facingMode: environment`) with a
  **Flip** button to switch. It decodes both 1D barcodes and QR codes; on a hit
  it shows the format and text, stops the camera, vibrates where supported, and
  offers **Copy** / **Scan again**.
- Camera access requires a secure context (HTTPS or `localhost`); the page shows
  a clear message if the camera or scanner library is unavailable.

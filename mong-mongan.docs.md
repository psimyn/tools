# Mong Mongan

A betting board game with 6 or 12 squares, showing either animals or coloured
shapes (triangles, squares and plus signs). Tap squares to put chips on them,
then roll. You can roll 3–6 dice whose faces match the board, or roll 1–3
balls across an uneven, curved tray and see which pockets they stop in.

## Prompt

> mong mongan game.
> create a board with either 6 or 12 squares, which can either be animals/figures, or colored shapes (triangle square and plus shape). option for either dice (3-6) or rolling a ball on ab uneven curved board and the ball lands on one of the symbols

## Notes

- **Boards**: 6 squares (3×2) or 12 squares (3×4). The shapes theme gives each
  row its own colour: red and blue for 6 squares, and red, blue, green and
  yellow for 12.
- **Betting**: you start with 50 chips. Tap a square to bet a chip on it, and
  long-press or right-click to take one back. Each die or ball that lands on
  your symbol pays your stake once (2 matches pay 2×). If none land there, you
  lose the stake. Bets stay on the board for the next roll, and a Refill button
  shows up when you run out. The bank and settings are saved in `localStorage`.
- **Dice**: 3–6 dice. Each one has a face for every square, so a 12-square
  board uses 12-sided dice.
- **Ball tray**: the board is a height field. Each square is a round pocket
  with low ridges between them. On top of that sits a random tilt, a
  bowl/dome curve, a twist and 4–7 bumps or dips, all drawn with hillshading.
  The balls are launched from the near edge and roll under gravity from the
  slope, with drag, rolling friction, bouncy walls and ball-to-ball
  collisions. A roll takes about 5 s. Since the tray is uneven, every board
  has a few lucky squares. **Reshape the board** makes a new random surface.
- `mongSim(n)` in the console runs `n` one-ball rolls instantly and returns
  how many landed on each square.

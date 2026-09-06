# Veil

A text editor that ciphers every character on the way in, so the screen only
ever shows the enciphered text — you type "meet me at the old bridge" and watch
"zrrg zr ng gur byq oevqtr" appear. Pick a cipher (ROT13, Atbash, ROT47, or
shuffle, which deals a fresh random alphabet on every keystroke), and hit
**reveal** when you actually want to read it back.

## Prompt

> a simple text editor, where it does a simple encode of your text as you type. so you never see unencrypted characters while typing. think of a suitable short name, ui super simple. just a text area
>
> can it shuffle all the letters on each keypress

## Notes

- **This is obfuscation, not encryption.** ROT13, Atbash and ROT47 are keyless
  classical ciphers, and shuffle keeps its alphabet in plain sight next to the
  text. It's shoulder-surfing cover, not secrecy.
- **The textarea holds nothing but ciphertext.** There is no shadow plaintext
  buffer. Every cipher here is an *involution* (`f(f(x)) === x`) and maps one
  character to exactly one character, which is what makes that possible:
  encoding and decoding are the same call, and offsets never shift, so the
  caret, selection and scroll position keep working on the visible text.
- **Input is intercepted at `beforeinput`**: typed characters, pasted text and
  dropped text are cancelled and re-inserted enciphered via
  `document.execCommand('insertText')` — deprecated, but the only way to write
  into a textarea while keeping native undo. Deletions, line breaks and
  undo/redo pass straight through: they only move ciphertext around, and `\n`
  ciphers to itself.
- **Shuffle mode** re-rolls its alphabet after every edit and re-renders the
  whole document, so the entire text churns on each keypress and no two frames
  share a substitution. The alphabet is a random *pairing* of the 26 letters
  (and of the 10 digits) rather than an arbitrary permutation — that keeps it
  an involution, so shuffle rides the same encode/decode path as the fixed
  ciphers. Lengths never change, so the caret, selection and scroll survive the
  rewrite.
- **Undo in shuffle mode is ours, not the browser's.** Native undo would
  restore ciphertext written under alphabets that no longer exist, which
  decodes to nonsense, so `Ctrl/Cmd+Z` and `Ctrl/Cmd+Shift+Z` are intercepted
  and served from a 200-deep stack of plaintext snapshots (re-enciphered under
  a fresh alphabet on the way back out). The other three modes keep native
  undo.
- **IME and predictive keyboards** compose in place, so the composition is left
  alone and the result is enciphered on `compositionend` (the composed text is
  briefly visible in the IME preview — unavoidable). Nothing is saved or
  re-shuffled mid-composition.
- **Reveal** is a toggle, not a peek: the textarea turns amber and read-only, so
  you still never type against plaintext. `Esc` hides it. **Copy** copies
  exactly what's on screen — ciphertext normally, plaintext while revealed.
- **Switching cipher** decodes with the outgoing cipher and re-encodes with the
  incoming one, so your text survives the change.
- Ciphertext (never plaintext) is autosaved to `localStorage`, along with the
  shuffle alphabet — without it the saved text would be unreadable after a
  reload. **Clear** wants a second click to confirm, and wipes both.
- ROT13 also rotates digits by 5, Atbash maps `0↔9`, and ROT47 scrambles
  punctuation as well. Non-ASCII characters pass through unchanged in every
  mode.
- No build step, no dependencies — a single `.html` file.

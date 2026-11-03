# NØVEX Character Kit — Explorer Base

This package contains a first-pass implementation of the character reference supplied in the conversation.

## Included
- Transparent PNG frames extracted from the supplied sprite sheet:
  - `assets/explorer/idle/` — 6 frames
  - `assets/explorer/run/` — 6 frames
  - `assets/explorer/jump/` — 6 frames
- `assets/explorer/manifest.json` — animation metadata
- `sprite-character.js` — lightweight Canvas sprite animation class
- `index.html` — local browser demo
- `assets/explorer/source_reference.jpeg` — original reference sheet

## Run locally
Serve this folder through a local HTTP server (ES modules and fetch require HTTP):
```bash
python -m http.server 8000
```
Then open `http://localhost:8000`.

## Integration notes
- Keep this as a self-contained module first; do not replace the existing renderer.
- Move `assets/explorer/` into the project's asset library and import `SpriteCharacter`.
- The current frame timing is a prototype baseline. Tune FPS and animation loops after visual review.
- The jump animation is configured as non-looping; call `setAnimation("idle")` or another animation when the action finishes.
- The supplied sheet's original numbered labels are excluded from extracted character frames.
- This is a female explorer reference asset. The engine itself is gender-neutral and can host future character manifests using the same schema.

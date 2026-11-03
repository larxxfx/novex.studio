# NØVEX Character System — Claude / Repository Instructions

Adopt the supplied Explorer sprite reference as the first character asset and implement the included prototype as a modular subsystem.

## Non-negotiable visual direction
- Use the provided Explorer reference as the canonical style reference.
- Preserve the hand-drawn 2D storybook look, expressive face, detailed clothing, muted palette, and dark illustrated outlines.
- Do not replace it with a geometric mascot, flat icon, generic emoji, or a different art style.
- The initial character is the female Explorer shown in the reference. The engine must support male/female character manifests later without hardcoding gender into the renderer.

## Implementation
1. Inspect the existing NØVEX repository and identify the current video renderer, asset pipeline, scene schema, and render entry point.
2. Integrate `sprite-character.js` and the `assets/explorer/` package as a separate module.
3. Keep existing production flows intact. Do not rewrite or remove the existing renderer.
4. Support transparent PNG frame sequences using the manifest schema.
5. Add animation states: `idle`, `run`, and `jump`; prepare the schema for future `walk`, `talk`, `point`, `look`, `wave`, `sit`, `crouch`, and `interact`.
6. Make animation timing deterministic and frame-accurate for offline video rendering. Do not rely exclusively on browser `requestAnimationFrame` for final MP4 export; expose a `renderFrame(timeMs)` or equivalent deterministic API for the server-side renderer.
7. Keep character position, scale, anchor, z-index, animation start time, and animation speed configurable per scene.
8. Add asset caching and preload all frames before rendering.
9. Add a scene-level example showing the character over a background.
10. Add tests for manifest loading, frame selection, animation looping, non-looping jump completion, and missing assets.

## Validation
- Run the repository's existing tests and build.
- Render a short sample clip using the actual NØVEX export pipeline.
- Verify transparent edges, no parchment remnants, no frame labels, no clipping, no character flicker, and correct timing.
- Report changed files, test results, sample render path, and any remaining limitations.

## Git workflow
- Work on a feature branch named `feat/novex-explorer-character`.
- Do not push directly to the default branch.
- Commit the character asset package and implementation with a descriptive commit message.
- Open a pull request for review.

# Motion Styles

A one-page field guide to 16 motion design styles. Each style has a looping 6-second animation made in After Effects or Blender, plus a short description.

## Run it

It's a static site with no build step:

```bash
python -m http.server 5520
```

Then open http://localhost:5520.

## Structure

| Path | What |
|---|---|
| `index.html`, `styles.css`, `main.js` | The page: hero, filterable grid, full-size viewer |
| `styles-data.js` | Name, tags, tool and description for every style (edit the text here) |
| `videos/web/` | Web-compressed loops (H.264, CRF 26, ~7 MB total) |
| `posters/` | One poster frame per loop |
| `ae/motion-styles.aep` | After Effects project for the 12 AE styles |
| `blender/` | Blender scenes and the Python scripts that build them (Clay 3D, Y2K Chrome, Isometric, Low Poly); `render_all.ps1` renders and encodes them |
| `tools/vsc.py` | Client for the local VS Code MCP bridge used to write the code |

## Re-rendering

- **After Effects:** `aerender -project ae/motion-styles.aep` writes full-quality MP4s to `videos/`.
- **Blender:** `blender/render_all.ps1`.
- **Web copies:** re-encode with `ffmpeg -i in.mp4 -an -c:v libx264 -crf 26 -pix_fmt yuv420p -movflags +faststart videos/web/out.mp4`.

The full renders are git-ignored because they can be regenerated.

## Styles

Swiss, Pop Art, Flat 2D, Clay 3D, Glassmorphism, Y2K Chrome, Synthwave, Risograph, Particle, Neo-Brutalism, Bauhaus, Vaporwave, Pixel Art, Isometric, Low Poly, Line Art.

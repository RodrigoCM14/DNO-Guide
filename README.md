# Digital Nexus Online Guide Project

This workspace contains a converted working draft of the DNO newbie guide.

## Files

- `DNO_Newbie_Guide.md` - first-pass Markdown conversion of the PDF, with a working table of contents and quick progression summary.
- `site/index.html` - searchable, hyperlinkable web guide.
- `site/styles.css` - green digital theme styling.
- `site/app.js` - guide search, result links, active navigation, and back-to-top behavior.
- `newbie-guide-extracted.txt` - raw text extracted from the original PDF.
- `pdf_metadata.json` - PDF source metadata.
- `make_guide.py` - repeatable converter used to rebuild the Markdown draft from the extracted text.
- `build_site.py` - repeatable site generator used to rebuild the web guide from the Markdown draft.

## Source

Original PDF:

`C:\Users\rcarr\Downloads\Newbie Guide [Extensive].pdf`

## Current Direction

The final format is a small searchable guide site in `site/`. It keeps the long converted draft as the detailed reference, then adds player-facing overview tables for:

1. Map unlocks.
2. Farming routes.
3. Progression milestones.
4. Dungeon routes.

The site also includes callouts for important warnings, requirements, notes, and time estimates.

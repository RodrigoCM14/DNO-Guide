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

## Next Editing Pass

Recommended next pass:

1. Turn map unlocks, farming routes, dungeon routes, and progression milestones into tables.
2. Add callouts for important warnings, prerequisites, and time estimates.
3. Split the long converted draft into player-facing sections.
4. Decide whether the final guide should become Markdown, a DOCX/PDF, or a small searchable guide site.

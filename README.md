# TechVestVentures Longevity Health Graphs

Public site: https://atlantean2.github.io/tvv-longevity-health-graphs/

A special graph collection published by the Longevity Strategies Project.
Every page is labeled **Not medical advice; published by the Longevity Strategies Project**.

Source deck: https://docs.google.com/presentation/d/1luWb64cNdOh-oY6yIQwZWTZ6tVYXsN3X/edit

## Monthly refresh

The Longevity Strategies Project refreshes the PNG folder on the 1st of each month.

1. Put the new 1600×901 PNGs and `index.csv` in:

   `/workspace/longevity-supplements/graphs-for-risk-watcher/`

   `index.csv` columns: `filename`, `category`, `title`, `guide_slide`, `source_urls`.
   Separate multiple source URLs with ` | ` (space, pipe, space). Every URL must be `https://`.
   Each category becomes one tab. The usual four are Mitochondria, Colds and Flu, Hair, and Throat Infections; a new category name is added as an extra tab.

2. From this folder, rebuild the site:

   ```bash
   python3 build.py
   ```

   To use a different assets folder:

   ```bash
   LONGEVITY_GRAPHS=/path/to/folder python3 build.py
   ```

3. Review the generated `index.html` and `issues/` pages. Then publish only the site output:

   ```bash
   git add index.html .nojekyll assets/style.css issues
   git -c user.name=Atlantean2 -c user.email=Atlantean2@users.noreply.github.com \
     commit -m "Longevity Health Graphs monthly refresh YYYY-MM"
   git push origin main
   ```

   Do not change Digest issues or other graph sites as part of a monthly refresh, unless the sidebar itself needs an update.

## Graph layout (2026-11-15)

`build.py` renders each graph at full width of the content column (column max 1500px, image 1600x901 webp straight from the source PNGs, not downscaled), one per row with no side-by-side thumbnail. Title and slide line sit directly below, followed by the source links in small (12px) wrapping text. Clicking a graph opens a full-screen lightbox (vanilla JS/CSS in `index.html`; closes on click or Esc); the image is wrapped in a link to the full-size file, so it still opens without JavaScript. The monthly refresh keeps all of this because it lives in `build.py` (`common.CSS` additions, `fig()`, `LIGHTBOX`). Chart content and titles are unchanged.

The shared left-column link lives in `/workspace/risk-watcher/tvv_nav.py` (`longevity` → this site). A full Digest or graph-site rebuild will pick it up; a sidebar-only update should patch each site's `index.html` nav block and leave `style.css` and issue pages untouched.

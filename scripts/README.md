# Scripts

These scripts make the ground truth of this repository from Wikisource. To
use the ground truth you need none of them, only `../get_images.sh` for the
page images.

## Requirements

- Python 3.9 or later, no extra packages
- Tesseract 5 with two models which read the typefaces of the work well
  (`tesseract` in the path, or set `TESSERACT=/path/to/tesseract`); the
  build needs the PAGE output (`tessedit_create_page_xml`)
- ImageMagick with DjVu support (`convert`), `pdftoppm`, `curl`

## The steps for a new work

Run them in this directory. `WORK` is the directory name of the work, for
example `vlenspiegel_1515`; `de` is the Wikisource.

| Step | Script | What it does |
|---|---|---|
| 1 | `ws-get-scan.py` | Downloads the scan file (DjVu or PDF) from Wikimedia Commons, checks its SHA-1 and writes `provenance/source.txt` and `scan.json`. |
| 2 | `ws-fetch-text.py` | Fetches the wikitext of every proofread page into `provenance/wikisource/`, with revision, time stamp and contributors. |
| 3 | `ws-build.py` | Recognises each page with two models, aligns the Wikisource text, restores the forms of the print and writes `GT-PAGE/*.xml` and `provenance/lines.tsv`. |
| 4 | `page-simplify.py` | Reduces the points of line polygons and baselines. |
| 5 | `ws-finish.py` | Writes `work.yml` and `CONTRIBUTORS.md`. |
| 6 | `ws-readme-table.py` | Rewrites the table of works in `../README.md` (run it in the repository root). |
| 7 | `ws-sample.py` | Makes a sheet of random line images with their texts, for checking by eye. |

```sh
W=../data/de/WORK
./ws-get-scan.py de.wikisource.org "File name.djvu" $W
./ws-fetch-text.py de.wikisource.org "File name.djvu" 1 LAST $W/provenance/wikisource
./ws-build.py $W WORK MODEL1 MODEL2 TESSDATA_DIR
./page-simplify.py --eps 1 $W/GT-PAGE/*.xml
./ws-finish.py $W "Title, place year" YEAR
(cd .. && scripts/ws-readme-table.py)
./ws-sample.py $W 12 /tmp/sample.jpg
```

"File name.djvu" is the name of the index on Wikisource, without `Index:`.
For a work with one image file per page, give `@FILES.txt` in its place in
steps 1 and 2: a list of the file names, one per line, in page order.

## Settings of `ws-build.py`

Environment variables, chosen per work after a look at the scans:

| Variable | Default | Meaning |
|---|---|---|
| `ZFORM` | `ʒ` | Form of the tailed z. Use `ZFORM=z` for prints after about 1530. |
| `LONGS` | `1` | `LONGS=0` for a print without long s (modern Antiqua): a long s read by the models then counts as s. |
| `ESZETT` | empty | `ESZETT=ſs` for a print which has no ß type and sets ſs for it. |
| `DPI` | `300` | Resolution of the page images of a PDF scan. Choose it so that the embedded scan is not scaled (`pdfimages -list`). It is stored in `provenance/source.txt`. |
| `MAXSUBST` | `2` | How many single letters per line may differ between a model and Wikisource (the letter of Wikisource is taken). |
| `TESSERACT` | `~/tess-next/build/bin/tesseract` | The Tesseract program. |

The table `PAIRS` at the top of `ws-build.py` lists which print forms may
stand for which normalised forms of Wikisource. A new work may need new
entries; the reasons in `provenance/lines.tsv` show what was not explained.
Wikisource templates which the script does not know are counted and printed
at the end; lines with them are left out until the template is handled in
`ws_lines()`.

After a change of the scripts, delete `GT-PAGE/*.xml` of a work and run
steps 3 to 6 again. The recognition is cached in `.ocr/`; delete that too
when the images or the models change.

## Looking for works

- `ws-survey.py` reads a dump of a Wikisource
  (`<lang>wikisource-latest-pages-articles.xml.bz2` from
  https://dumps.wikimedia.org/) and lists every scan file with year, pages,
  proofread levels and signs of print forms. No requests to the API.
- `ws-typeface.py` and `ws-typeface2.py` fetch one or two page images per
  work and tell Fraktur from Antiqua by the share of long s.

## Requests to Wikimedia

All requests go through `wsapi.py`: one at a time, a pause of four seconds
after each, and waiting when the server answers with HTTP 429. Please keep
it that way and do not run several fetches in parallel; Wikimedia limits
automated requests. The scan file of a work is downloaded once.

The file server of Wikimedia Commons limits downloads of original files:
after about ten in two minutes it answers HTTP 429 with `Retry-After: 600`.
For works with one image file per page `ws-get-scan.py` therefore fetches
one image every 90 seconds (`PACE`) and waits as long as the server says
when it is refused. Several hundred pages take many hours.

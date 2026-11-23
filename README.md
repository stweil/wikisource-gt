# wikisource-gt

Line ground truth for OCR training, made from proofread texts of
[Wikisource](https://wikisource.org/) and the scans they were transcribed
from. Each page is a PAGE XML file with line polygons, baselines and text.
The page images are not part of the repository; `get_images.sh` downloads
them.

**State: pilot.** The method and the rules below may still change.

## Content

`data/<wikisource>/<work>/`, one directory level per Wikisource (`de` for
de.wikisource.org, `la` for la.wikisource.org, ...):

| Directory | Work | Pages | Lines used | Lines left out |
|---|---|---|---|---|
| `de/rosengarten_1515` | Eucharius Rößlin: Der Swangern frawen vnd hebammen roszgarten, 1515 | 100 | 1,434 | 1,938 |
| `de/vlenspiegel_1515` | Ein kurtzweilig lesen von Dyl Vlenspiegel, Straßburg 1515 | 252 | 2,381 | 3,014 |
| `de/schachzabel_1520` | Jakob Köbel: Schachzabel Spiel, Oppenheim 1520 | 43 | 717 | 511 |
| `de/bergbuechlin_1527` | Ein nützlich Bergbüchlin, 1527 | 46 | 677 | 487 |
| `de/teuffel_1589` | Hansen Schmidt Teuffel, 1589 | 23 | 429 | 314 |
| `de/restitutionsedikt_1629` | Restitutionsedikt, 1629 | 28 | 348 | 708 |
| `de/pralerey_1673` | Deß Weltberuffenen Simplicissimi Pralerey und Gepräng mit seinem Teutschen Michel, 1673 | 121 | 1,879 | 1,385 |
| `de/wundergesicht_1678` | Weißenfelsisches Wunder-Gesicht, 1678 | 35 | 754 | 524 |
| `de/feurordnung_1681` | Revidirte Feur-Ordnung, Hannover 1681 | 25 | 435 | 246 |
| `de/friedensinstrument_1697` | Friedens-Instrument zu Ryswick, 1697 | 34 | 437 | 915 |
| | **Total** | **707** | **9,491** | **10,042** |

The layout follows the [OCR-D template for ground truth
repositories](https://github.com/OCR-D/gt-repo-template): `METADATA.yml` and
`LICENSE.md` in the root, `data/.../GT-PAGE/` for the PAGE files.

Different from the template: the page images are downloaded by
`get_images.sh`, there is one more directory level per Wikisource
(`data/de/...`), each work has a `provenance/` directory, and the template's
GitHub workflow is not used; the README is written by hand.

In each work directory:

- `GT-PAGE/*.xml` – the ground truth.
- `work.yml` – data of the work (title, year, sources, models, counts).
- `CONTRIBUTORS.md` – the Wikisource users who edited the pages.
- `provenance/` – what the ground truth was made from:
  - `wikisource/*.json`: the Wikisource page texts as fetched (wikitext,
    revision, time stamp, proofread level, contributors);
  - `lines.tsv`: every recognised line, used or left out, the reason, the
    stretch of Wikisource, both recognitions and the final text;
  - `source.txt`, `scan.json`: URL, SHA-1 and licence of the scan file.

## How the text is made

Wikisource texts are proofread twice, but their spelling is normalised: the
German Wikisource writes round s for long s, expands abbreviations (`vnd`
for `vñ`, `truncken` for `trunckẽ`, `der` for `ð`), writes r for r rotunda
and moves split words to the next line. A line image shows the forms of the
print, so the text is processed (`scripts/ws-build.py`):

1. The page scan is recognised with two Tesseract models. This gives the
   lines (polygon, baseline) and two readings of each.
2. The Wikisource text of the page is aligned with each reading, and every
   recognised line gets its stretch of that text. The line breaks are those
   of the print.
3. The two are compared letter by letter. A difference is accepted only
   where it is a known pair of print form and normalised form (long s / s,
   r rotunda / r, vowel with bar / vowel + n or m, `ñ` / nn or nd, `ð` /
   der, ...). The text gets the letters of Wikisource and the print forms
   of the recognition. Where a model reads one plain letter as another, the
   letter of Wikisource is taken (at most twice per line).
4. A line is used only if both models lead to exactly the same text. All
   other lines are left out.

Nothing is lost: a line which is left out stays in the PAGE file as an XML
comment (polygon, baseline, reason, Wikisource stretch, both readings), and
the whole Wikisource text of the page is a comment at the end of the file.
Such lines can be completed by hand.

The method cannot see an error which both models make in the same way at a
print form. Samples of 9 to 12 random lines per work were compared with
the images (about 70 lines in all); a larger check is still to be done.

## Transcription rules

The texts follow the [OCR-D ground truth guidelines, level
2](https://ocr-d.de/en/gt-guidelines/trans/), with the conventions used in
the other ground truth repositories of UB Mannheim:

- Long s (`ſ`) and round s as printed; `ß` for the ligature of long s and z.
- r rotunda as `ꝛ`.
- Abbreviations are kept, not expanded. A bar or wavy line above a letter is
  a tilde (U+0303, in composed form where Unicode has one: `ẽ`, `ñ`).
  Other signs as printed: `ð` (d with a stroke for "der"), `ꝰ`, `ꝑ`.
- Historic umlauts as printed: small e above (`aͤ oͤ uͤ`, letter + U+0364
  COMBINING LATIN SMALL LETTER E), u with small o above as `uͦ` (u + U+0366
  COMBINING LATIN SMALL LETTER O, the OCR-D form; not U+016F LATIN SMALL
  LETTER U WITH RING ABOVE), and `ä ö ü` where the print has two dots or
  strokes.
- u/v and i/j as printed. I and J in Fraktur by sound.
- `æ` and `œ` are not split.
- Virgule: directly after the word, followed by a blank (`ward/ vnd`).
  Wikisource puts blanks on both sides.
- Hyphens as they look: the double hyphen of Fraktur is `⸗`. A word split
  at the line end without a sign has none in the text.
- Raised small digits are superscripts.
- Misprints are kept. Where Wikisource corrects one and gives the printed
  form in a note, the printed form is used.
- The tailed z of early prints is written `ʒ` (U+0292), as in the
  Kallimachos part of GT4HistOCR. The OCR-D guidelines have no rule for it;
  `ʒ` can always be normalised to `z`, the reverse is not possible. Set per
  work (`ZFORM` in `ws-build.py`).

Different from Wikisource, therefore: long s, r rotunda, tailed z,
abbreviations, line breaks, the virgule.

## Images

    ./get_images.sh            # all works
    ./get_images.sh de/vlenspiegel_1515

downloads the scan file of each work from Wikimedia Commons (one request per
work, checked by SHA-1) and writes the page images next to the PAGE files.
It needs `curl`, ImageMagick with DjVu support and `pdftoppm`.

## Adding a work

See [scripts/README.md](scripts/README.md) for the scripts, their order and
their settings.

## Licence

- Text: from Wikisource, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
  The contributors of each work are listed in its `CONTRIBUTORS.md`; each
  PAGE file names the page and revision it was made from. The changes
  described above were made by Mannheim University Library.
- Scans: see the file page on Wikimedia Commons named in `work.yml`
  (public domain for the works so far).
- Scripts (`scripts/`, `get_images.sh`): Apache License 2.0,
  https://www.apache.org/licenses/LICENSE-2.0. `LICENSE.md` is the licence of
  the data.

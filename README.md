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
| `de/narrenschiff_1499` | Sebastian Brant: Das Narrenschiff, Basel 1499 | 307 | 2,860 | 5,188 |
| `de/rosengarten_1515` | Eucharius Rößlin: Der Swangern frawen vnd hebammen roszgarten, 1515 | 100 | 1,432 | 1,940 |
| `de/vlenspiegel_1515` | Ein kurtzweilig lesen von Dyl Vlenspiegel, Straßburg 1515 | 252 | 2,376 | 3,019 |
| `de/schachzabel_1520` | Jakob Köbel: Schachzabel Spiel, Oppenheim 1520 | 43 | 716 | 512 |
| `de/bergbuechlin_1527` | Ein nützlich Bergbüchlin, 1527 | 46 | 675 | 489 |
| `de/carolina_1533` | Keyser Karls des fünfften vnnd des heyligen Römischen Reichs peinlich gerichts ordnung (Constitutio criminalis Carolina), Mainz 1533 | 108 | 1,614 | 2,123 |
| `de/teuffel_1589` | Hansen Schmidt Teuffel, 1589 | 23 | 429 | 314 |
| `de/restitutionsedikt_1629` | Restitutionsedikt, 1629 | 28 | 330 | 726 |
| `de/pralerey_1673` | Deß Weltberuffenen Simplicissimi Pralerey und Gepräng mit seinem Teutschen Michel, 1673 | 121 | 1,869 | 1,395 |
| `de/wundergesicht_1678` | Weißenfelsisches Wunder-Gesicht, 1678 | 35 | 754 | 524 |
| `de/feurordnung_1681` | Revidirte Feur-Ordnung, Hannover 1681 | 25 | 435 | 246 |
| `de/friedensinstrument_1697` | Friedens-Instrument zu Ryswick, 1697 | 34 | 436 | 916 |
| `de/dalimil_chronik_1859` | Dalimils Chronik von Böhmen | 30 | 1,010 | 173 |
| `de/schiller_galerie_1859` | Friedrich Pecht: Schiller-Galerie | 30 | 756 | 201 |
| `de/album_schloesser_rittergueter_1860` | Gustav Adolf Pönicke (Hrsg.): Album der Rittergüter und Schlösser im Königreiche Sachsen I. Section | 22 | 983 | 491 |
| `de/spiess_lahnthal_1866` | August Spieß: Das Lahntal von seinem Ursprung bis zur Ausmündung nebst seiner nächsten Umgebung | 30 | 890 | 194 |
| `de/newton_principien_1872` | Isaac Newton: Mathematische Principien der Naturlehre | 30 | 1,041 | 301 |
| `de/darwin_entstehung_1876` | Charles Darwin: Über die Entstehung der Arten | 30 | 844 | 316 |
| `de/chemnitz_1878` | Mitteilungen des Vereins für Chemnitzer Geschichte, Erster Band, Chemnitz 1878 | 353 | 8,742 | 7,230 |
| `de/chemnitz_1883` | Mitteilungen des Vereins für Chemnitzer Geschichte, Dritter und Vierter Band, Chemnitz 1883 | 426 | 9,506 | 9,448 |
| `de/schmidt_miscellanea_silurica_1883` | Friedrich Schmidt: Miscellanea silurica III | 30 | 894 | 254 |
| `de/georgien_natur_sitten_1885` | Arthur Leist: Georgien. Natur, Sitten und Bewohner | 30 | 864 | 212 |
| `de/hans_schiltbergers_reisebuch_1885` | Valentin Langmantel (Hrsg.): Hans Schiltbergers Reisebuch nach der Nürnberger Handschrift | 16 | 577 | 193 |
| `de/kunstdenkmaeler_floeha_1886` | Richard Steche: Kunstdenkmäler Amtshauptmannschaft Flöha | 30 | 870 | 550 |
| `de/patkanjan_erzaehlungen_1886` | Rafael Patkanjan: Drei Erzählungen | 30 | 785 | 89 |
| `de/woermann_gemaeldegalerie_1887` | Katalog der Königlichen Gemäldegalerie zu Dresden (1887) | 30 | 506 | 840 |
| `de/krohn_baer_wolf_1889` | Kaarle Krohn: Bär (Wolf) und Fuchs | 30 | 714 | 363 |
| `de/galeriewerk_luecke_1894` | Hermann Lücke: Die Königliche Gemäldegalerie zu Dresden | 30 | 847 | 263 |
| `de/klarissen_neuss_1896` | Urkunden und Akten aus dem Archiv der Klarissen zu Neuss | 30 | 1,069 | 300 |
| `de/jahrbuch_radfahrer_1897` | Jahrbuch der deutschen Radfahrer-Vereine mit Beiträgen hervorragender Fachschriftsteller und unter Mitwirkung der Vereine selbst | 29 | 962 | 1,160 |
| `de/touren_buch_estland_1897` | C.I. Dethloff, Alph. Krause: Touren-Buch von Estland mit Fortführung der Touren bis in die Städte Nord-Livlands | 17 | 535 | 206 |
| `de/cistercienser_heiligenkreuz_1898` | Florian Watzl: Die Cistercienser von Heiligenkreuz | 30 | 1,014 | 352 |
| `de/malerwerke_band2_1898` | Malerwerke des neunzehnten Jahrhunderts – Zweiter Band | 30 | 2,058 | 1,822 |
| `de/zauberwesen_hexenwahn_niederrhein_1898` | Emil Pauls: Zauberwesen und Hexenwahn am Niederrhein. In: Beiträge zur Geschichte des Niederrheins, Jahrbuch des Düsseldorfer Geschichtsvereins. 13. Band, 1898. S. 134-242 | 30 | 791 | 658 |
| `de/josephus_altertuemer_1899` | Jüdische Altertümer | 30 | 910 | 226 |
| `de/moebius_schwachsinn_1903` | Über den physiologischen Schwachsinn des Weibes. 5. veränderte Auflage | 30 | 1,025 | 173 |
| `de/gurlitt_kunstdenkmaeler_dresden_1904` | Cornelius Gurlitt: Die Kunstdenkmäler von Dresdens Umgebung. Theil II Amtshauptmannschaft Dresden-Neustadt | 30 | 1,054 | 527 |
| `de/zehnte_muse_1904` | Die zehnte Muse | 30 | 691 | 525 |
| `de/hegel_phaenomenologie_1907` | Phänomenologie des Geistes | 30 | 1,152 | 164 |
| `de/aarne_maerchenforschungen_1908` | Antti Aarne: Vergleichende Märchenforschungen | 30 | 742 | 540 |
| `de/schumann_dresden_1909` | Paul Schumann: Dresden. Berühmte Kunststätten, Band 46, 1. Auflage | 30 | 1,001 | 215 |
| `de/friedlaender_kriminalprozesse_1910` | Hugo Friedländer: Interessante Kriminal-Prozesse von kulturhistorischer Bedeutung, Band 1 | 30 | 875 | 207 |
| `de/adler_nervoes_1912` | Alfred Adler: Über den nervösen Charakter | 30 | 1,349 | 196 |
| `de/sophienkirche_dresden_1912` | Robert Bruck: Die Sophienkirche in Dresden | 30 | 428 | 731 |
| `de/knortz_hexen_teufel_1913` | Karl Knortz: Hexen, Teufel und Blocksbergspuk in Geschichte, Sage und Literatur | 30 | 973 | 237 |
| `de/otto_herodes_1913` | Walter Otto: Herodes. Beiträge zur Geschichte des letzten jüdischen Königshauses | 7 | 324 | 448 |
| `de/handbuch_politik_band1_1914` | Handbuch der Politik – Band 1 | 30 | 970 | 563 |
| `de/jensen_schewtschenko_1916` | Alfred Anton Jensen: Taras Schewtschenko. Ein ukrainisches Dichterleben | 30 | 686 | 463 |
| `de/dresden_geschichte_heft26_1918` | Kurt Kreiser: Carl Gottlieb Reissiger. Sein Leben nebst einigen Beiträgen zur Geschichte des Konzertwesens in Dresden | 29 | 553 | 998 |
| `de/eroberung_brotes_1919` | Pjotr Alexejewitsch Kropotkin, Bernhard Kampffmeyer (Übersetzer): Die Eroberung des Brotes | 30 | 1,017 | 340 |
| `de/richter_verzeichnis_1922` | Johann Friedrich Hoff; Karl Budde: Adrian Ludwig Richter, Maler und Radierer. Verzeichnis seines gesamten graphischen Werkes | 29 | 626 | 773 |
| `de/cassirer_symbolische_formen_1923` | Ernst Cassirer: Philosophie der symbolischen Formen, erster Teil | 30 | 854 | 330 |
| `de/haenel_kostbare_waffen_1923` | Erich Haenel: Kostbare Waffen aus der Dresdner Rüstkammer | 30 | 464 | 651 |
| `de/hexenhammer_1923` | Jakob Sprenger, Heinrich Institoris; J. W. R. Schmidt (Übersetzung): Der Hexenhammer | 30 | 1,068 | 136 |
| `de/ossendowski_schatten_dunklen_1924` | Antoni Ferdinand Ossendowski: Schatten des dunklen Ostens | 30 | 635 | 400 |
| `de/schnitzler_traumnovelle_1926` | Traumnovelle | 30 | 702 | 141 |
| `de/sponsel_gruenes_gewoelbe_1928` | Jean Louis Sponsel: Das Grüne Gewölbe: eine Auswahl von Meisterwerken in vier Bänden. Band 2 | 30 | 781 | 518 |
| `de/freud_vorlesungen_1933` | Neue Folge der Vorlesungen zur Einführung in die Psychoanalyse | 30 | 828 | 109 |
| `de/philo_traeume_1938` | Über die Träume (De somnis) übersetzt von Maximilian Adler | 30 | 709 | 520 |
| `de/loos_schriften_1962` | Adolf Loos: Adolf Loos – Sämtliche Schriften | 30 | 829 | 120 |
| | **Total** | **3,220** | **71,430** | **53,259** |

**Evaluation data:** the two volumes of the *Mitteilungen des Vereins für
Chemnitzer Geschichte* (`de/chemnitz_1878`, `de/chemnitz_1883`, modern
Antiqua) are used to evaluate models and should be kept out of training
(`role: evaluation` in their `work.yml`).

**Modern Antiqua:** of the works printed in Antiqua from 1859 to 1962 only a
selection of up to 30 pages per work is used, spread evenly over the work
(`scripts/ws-select-pages.py`; proofread pages with at least 1,200
characters, of a series only one volume). This keeps the repository small
and still gives many typefaces.

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
   letter of Wikisource is taken (at most twice per line). With `STRICT=1`
   (used for Narrenschiff 1499 and Carolina 1533) the line is left out
   instead when both models read the same other letter there: in a sample
   that was nearly always a place where Wikisource differs from the print.
4. A line is used only if both models lead to exactly the same text. All
   other lines are left out.
5. The layout analysis sometimes cuts a printed line into pieces. A piece
   whose text starts or ends inside a word is left out.

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
Two works have one image file per page (`de/narrenschiff_1499`,
`de/carolina_1533`); Wikimedia Commons refuses fast downloads of original
files, so these are fetched at one image every 90 seconds (about 8 and 3
hours).
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

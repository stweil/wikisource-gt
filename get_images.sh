#!/bin/bash
# Download the scan file of each work from Wikimedia Commons and write the
# page images next to the PAGE files (data/<wikisource>/<work>/GT-PAGE/).
# usage: get_images.sh [<wikisource>/<work> ...]
# Needs curl, ImageMagick with DjVu support and pdftoppm. One request per work;
# works with one image file per page: one request every 90 seconds, because
# Wikimedia Commons refuses faster downloads of original files (HTTP 429).
set -e
cd "$(dirname "$0")/data"
UA="wikisource-gt/0.1 (https://github.com/stweil/wikisource-gt)"
works=("$@"); [ ${#works[@]} -eq 0 ] && works=(*/*)
for w in "${works[@]}"; do
  [ -f "$w/provenance/source.txt" ] || continue
  if [ "$(wc -l < "$w/provenance/source.txt")" -gt 1 ]; then      # one image file per page
    while read -r url sha1 img; do
      f="$w/GT-PAGE/$img"
      [ -e "${f%.*}.xml" ] || continue
      if [ ! -s "$f" ]; then
        for try in 1 2 3 4 5 6; do
          curl -sS -f -L -A "$UA" -o "$f" "$url" && break
          rm -f "$f"; echo "$img: refused, waiting 10 minutes" >&2; sleep 600
        done
        sleep 90
      fi
      echo "$sha1  $f" | sha1sum -c --quiet -
    done < "$w/provenance/source.txt"
    continue
  fi
  read -r url sha1 name dpi < "$w/provenance/source.txt"
  f="$w/$(basename "$url")"
  if [ ! -s "$f" ]; then curl -sS -L -A "$UA" -o "$f" "$url"; sleep 5; fi
  echo "$sha1  $f" | sha1sum -c -
  dir=$(cd "$w" && pwd)
  for xml in "$w"/GT-PAGE/*.xml; do
    png=${xml%.xml}.png; [ -s "$png" ] && continue
    n=$(basename "$png" .png); n=$((10#${n##*_}))
    # ImageMagick sometimes fails on a DjVu page ("recursive opening") and
    # when the file is given with a path: run it in the directory and retry.
    for try in 1 2 3 4 5 6 7 8; do
      case "$f" in
        *.pdf) (cd "$dir" && pdftoppm -r "${dpi:-300}" -gray -png -f $n -l $n -singlefile "$(basename "$f")" "GT-PAGE/$(basename "$png" .png)" 2> /dev/null) ;;
        *) (cd "$dir" && convert "$(basename "$f")[$((n - 1))]" "GT-PAGE/$(basename "$png")" 2> /dev/null) ;;
      esac
      [ -s "$png" ] && break
      rm -f "$png"
    done
    [ -s "$png" ] || echo "no image for $xml" >&2
  done
done

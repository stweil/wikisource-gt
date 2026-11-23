"""Small helper for the Wikisource/Commons API: one request at a time, a pause
after each, and waiting when the server says so (HTTP 429)."""
import json, time, urllib.error, urllib.parse, urllib.request

UA = 'ocr-training-data-experiment/0.1 (line images and text for OCR training)'
PAUSE = 4.0

def get(url, binary=False):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            time.sleep(PAUSE)
            return data if binary else json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            wait = int(e.headers.get('Retry-After') or 60)
            time.sleep(wait)
    raise SystemExit('still rate limited, giving up')

def api(site, **params):
    params.update(format='json', formatversion='2')
    return get(f'https://{site}/w/api.php?' + urllib.parse.urlencode(params))

import os
import time
import requests
import csv
from jiwer import wer

BASE_URL = 'http://127.0.0.1:8000/transcribe'
TEST_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'test')
TEST_DIR = os.path.abspath(TEST_DIR)
REF_FILE = os.path.join(TEST_DIR, 'references.txt')
OUTPUT_CSV = os.path.join(TEST_DIR, 'results.csv')
MODEL = 'wav2vec2-base'

# Read references
refs = {}
if os.path.exists(REF_FILE):
    with open(REF_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                refs[parts[0]] = parts[1]

wav_files = [f for f in os.listdir(TEST_DIR) if f.lower().endswith('.wav')]
if not wav_files:
    print('No WAV files found in', TEST_DIR)
    raise SystemExit(1)

rows = []
for wf in wav_files:
    path = os.path.join(TEST_DIR, wf)
    print('Posting', wf)
    with open(path, 'rb') as fh:
        start = time.time()
        try:
            r = requests.post(f'{BASE_URL}?model={MODEL}', files={'file': (wf, fh, 'audio/wav')}, timeout=120)
        except Exception as e:
            print('Request failed for', wf, e)
            rows.append({'file': wf, 'error': str(e)})
            continue
        elapsed = time.time() - start
        if r.status_code != 200:
            print('Server error for', wf, r.status_code, r.text)
            rows.append({'file': wf, 'error': r.text, 'status': r.status_code})
            continue
        data = r.json()
        text = data.get('text') or data.get('transcription') or ''
        ref = refs.get(wf, '')
        score = None
        if ref:
            try:
                score = wer(ref, text)
            except Exception as e:
                score = None
        rows.append({'file': wf, 'text': text, 'reference': ref, 'wer': score, 'time_s': elapsed, 'model': MODEL})
        print(f"{wf}: {len(text)} chars, wer={score}, time={elapsed:.2f}s")

# Save results
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvf:
    writer = csv.DictWriter(csvf, fieldnames=['file','model','text','reference','wer','time_s','error','status'])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print('Wrote results to', OUTPUT_CSV)

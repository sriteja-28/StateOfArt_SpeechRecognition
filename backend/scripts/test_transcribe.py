import requests
fpath = 'data/test/eng1.wav'
print('Posting', fpath)
with open(fpath,'rb') as f:
    r = requests.post('http://127.0.0.1:8000/transcribe?model=wav2vec2-base', files={'file': ('eng1.wav', f, 'audio/wav')})
    print('Status:', r.status_code)
    try:
        print('JSON:', r.json())
    except Exception:
        print('Response text:', r.text)

import os
import numpy as np
import soundfile as sf

out_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'test')
os.makedirs(out_dir, exist_ok=True)

sample_rate = 16000

def write_sine(path, freq=440, duration=2.0):
    t = np.linspace(0, duration, int(sample_rate*duration), endpoint=False)
    data = 0.2 * np.sin(2 * np.pi * freq * t)
    sf.write(path, data, sample_rate)

# Generate a few small files
files = [
    ('eng1.wav', 440),
    ('eng2.wav', 554),
    ('spanish1.wav', 660),
    ('french1.wav', 880),
]

for name, freq in files:
    p = os.path.join(out_dir, name)
    write_sine(p, freq=freq, duration=3.0)
    print('Wrote', p)

# Create a simple references file
refs = {
    'eng1.wav': 'this is a test',
    'eng2.wav': 'another test sample',
    'spanish1.wav': 'prueba en espanol',
    'french1.wav': 'essai en francais'
}

with open(os.path.join(out_dir, 'references.txt'), 'w', encoding='utf-8') as f:
    for k, v in refs.items():
        f.write(f"{k}\t{v}\n")
print('Wrote references.txt')
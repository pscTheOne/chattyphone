# generate_dtmf_wavs.py

import numpy as np
import soundfile as sf

def generate_dtmf_tone(key, duration=5.0, fs=16000):
    dtmf_freqs = {
        '1': (697, 1209), '2': (697, 1336), '3': (697, 1477),
        '4': (770, 1209), '5': (770, 1336), '6': (770, 1477),
        '7': (852, 1209), '8': (852, 1336), '9': (852, 1477),
        '*': (941, 1209), '0': (941, 1336), '#': (941, 1477),
        'A': (697, 1633), 'B': (770, 1633), 'C': (852, 1633), 'D': (941, 1633)
    }

    if key not in dtmf_freqs:
        return None

    f1, f2 = dtmf_freqs[key]
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    tone = 0.5 * (np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t))
    return tone

def save_dtmf_tone(key, duration=5.0, fs=16000):
    tone = generate_dtmf_tone(key, duration, fs)
    if tone is not None:
        sf.write(f'dtmf_{key}.wav', tone, fs)

if __name__ == '__main__':
    keys = '1234567890*#ABCD'
    for key in keys:
        save_dtmf_tone(key)

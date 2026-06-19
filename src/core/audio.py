"""Audio: synthesized SFX + ambient background via pygame.mixer."""

import array
import math
import pygame

RATE = 44100
_sounds = {}
_music_ch = None
_muted = False
_ok = False


def pre_init():
    pygame.mixer.pre_init(RATE, -16, 1, 512)


def _tone(freq, dur, vol=0.3):
    n = int(RATE * dur)
    fade = max(1, min(n // 5, int(RATE * 0.02)))
    return array.array('h', (
        int(math.sin(2 * math.pi * freq * i / RATE) * vol * 32767
            * min(1, i / fade) * min(1, (n - i) / fade))
        for i in range(n)
    ))


def _chirp(f0, f1, dur, vol=0.3):
    n = int(RATE * dur)
    fade = max(1, min(n // 5, int(RATE * 0.02)))
    return array.array('h', (
        int(math.sin(2 * math.pi * (f0 + (f1 - f0) * i / n) * i / RATE)
            * vol * 32767 * min(1, i / fade) * min(1, (n - i) / fade))
        for i in range(n)
    ))


def init():
    global _ok
    try:
        _sounds['place'] = pygame.mixer.Sound(buffer=_chirp(400, 900, 0.1, 0.25))
        _sounds['delete'] = pygame.mixer.Sound(buffer=_chirp(600, 200, 0.12, 0.25))
        _sounds['click'] = pygame.mixer.Sound(buffer=_tone(800, 0.04, 0.15))

        win = array.array('h')
        for f in [523, 659, 784, 1047]:
            win.extend(_tone(f, 0.15, 0.3))
        _sounds['win'] = pygame.mixer.Sound(buffer=win)

        # Rhythmic pad: Cmaj7 arpeggio at 120 BPM, 4s seamless loop
        n = RATE * 4
        fade = RATE // 2
        freqs = [261.6, 329.6, 392.0, 493.9]
        bps = 2
        buf = array.array('h')
        for i in range(n):
            t = i / RATE
            val = 0
            for k, f in enumerate(freqs):
                beat_t = (t - k / (len(freqs) * bps)) % (1 / bps)
                val += math.sin(2 * math.pi * f * t) * math.exp(-beat_t * 8) * 0.05
            val += sum(math.sin(2 * math.pi * f * t) for f in freqs) / len(freqs) * 0.012
            cf = min(i, n - i, fade) / fade
            buf.append(max(-32767, min(32767, int(val * cf * 32767))))
        _sounds['music'] = pygame.mixer.Sound(buffer=buf)
        _ok = True
    except Exception:
        pass


def play_sfx(name):
    if _ok and not _muted and name in _sounds:
        _sounds[name].play()


def play_music():
    global _music_ch
    if _ok and 'music' in _sounds:
        _music_ch = _sounds['music'].play(loops=-1)


def stop_music():
    global _music_ch
    if _music_ch:
        _music_ch.stop()
        _music_ch = None


def toggle_mute():
    global _muted
    _muted = not _muted
    if _muted:
        stop_music()
    else:
        play_music()
    return _muted

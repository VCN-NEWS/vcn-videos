"""Outils d'analyse de voix sans reconnaissance vocale : empreinte spectrale pour repérer
une phrase répétée au raccord, et test de fin coupée."""
import subprocess, sys, numpy as np
SR = 16000

def load(f, ss=None, to=None):
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", str(ss)] if ss is not None else []) + (["-to", str(to)] if to is not None else []) + ["-i", f, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.int16).astype(float) / 32768

def feats(a, hop=160, win=400, nb=24):
    n = 1 + (len(a) - win) // hop
    fr = np.stack([a[i*hop:i*hop+win] * np.hanning(win) for i in range(max(n, 1))])
    sp = np.abs(np.fft.rfft(fr, 512))[:, 4:200]
    bands = np.array_split(sp, nb, axis=1)
    m = np.log(np.stack([b.mean(1) for b in bands], 1) + 1e-6)
    return (m - m.mean(0)) / (m.std(0) + 1e-6)

def best_match(needle, hay):
    """Similarité max (0..1) de needle glissé dans hay, et position (s)."""
    A, B = feats(needle), feats(hay)
    L = len(A); best = (-1, 0)
    for i in range(0, len(B) - L + 1):
        c = np.mean(np.sum(A * B[i:i+L], 1) / (np.linalg.norm(A, axis=1) * np.linalg.norm(B[i:i+L], axis=1) + 1e-9))
        if c > best[0]: best = (c, i * 0.01)
    return best

def tail_db(f, last=0.2):
    a = load(f); x = a[-int(SR*last):]
    return 20*np.log10(np.sqrt(np.mean(x**2)) + 1e-9)

if __name__ == "__main__":
    print(tail_db(sys.argv[1]))


def voice_cut_in_video(video, voice_mp3, lead):
    """Renvoie le moment (s, dans la voix) où la voix disparaît de la vidéo finale, ou None si elle est entière.
    OBLIGATOIRE après chaque mixage : un mixage raté peut couper les dernières secondes de narration."""
    vid, voice = load(video), load(voice_mp3)
    n = int(SR * 0.1)
    db = lambda a, i: 20 * np.log10(np.sqrt(np.mean(a[i:i + n] ** 2)) + 1e-9)
    for t in np.arange(0, len(voice) / SR - 0.1, 0.1):
        i, j = int(SR * t), int(SR * (t + lead))
        ev = db(voice, i)
        vv = db(vid, j) if j + n < len(vid) else -99
        if ev > -25 and vv < ev - 6:
            return round(t, 1)
    return None

"""Contrôle « mots avalés » plus fin : compte les noyaux syllabiques (pics d'énergie 300-3000 Hz) de chaque phrase
dans la voix finale et compare au nombre de syllabes écrites. Usage : python3 syllabes.py clé3"""
import sys, re, json
import numpy as np
from scipy.signal import butter, sosfiltfilt, find_peaks
import audiocheck as ac, videos

VOW = re.compile(r"[aeiouyàâäéèêëîïôöùûüœæ]+", re.I)


def nuclei(x, sr=ac.SR):
    sos = butter(4, [300, 3000], "band", fs=sr, output="sos")
    e = np.abs(sosfiltfilt(sos, x))
    k = int(0.02 * sr)
    env = np.convolve(e, np.ones(k) / k, "same")[:: int(sr * 0.005)]  # 5 ms
    env = 20 * np.log10(env + 1e-6)
    pk, _ = find_peaks(env, prominence=4, distance=16, height=env.max() - 35)  # >= 80 ms entre syllabes
    return len(pk)


def main(key):
    v = videos.VIDEOS[key]()
    a = ac.load(f"{videos.D}/voix_{key}.mp3")
    rows = []
    for i, s in enumerate(v.sent):
        t0, t1 = v.st[i]
        t0, t1 = t0 - v.lead, t1 - v.lead
        seg = a[int(max(0, t0 - 0.05) * ac.SR): int((t1 + 0.05) * ac.SR)]
        n = nuclei(seg) if len(seg) > 800 else 0
        exp = len(VOW.findall(s))
        rows.append((i, s[:45], exp, n, round(n / max(1, exp), 2)))
    r = np.array([x[4] for x in rows])
    med = float(np.median(r))
    low = [x for x in rows if x[4] < 0.7 * med and x[2] >= 5]
    print(json.dumps({"cle": key, "ratio_median": round(med, 2), "phrases_suspectes": low}, ensure_ascii=False))


if __name__ == "__main__":
    for k in sys.argv[1:]:
        main(k)

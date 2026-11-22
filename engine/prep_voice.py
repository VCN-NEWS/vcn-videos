"""Prépare la voix v3 : coupe le MP3 Hedra au début du blanc qui précède la phrase sacrifiée « Allez, ciao »,
retire les blancs et accélère de 10 % (PIPELINE.md). Usage : python3 prep_voice.py clé [clé…]"""
import sys, re, subprocess, json
import audiocheck as ac

def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)

def sil(f, n=-35, d=0.25):
    out = subprocess.run(["ffmpeg", "-i", f, "-af", f"silencedetect=n={n}dB:d={d}", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(st, en + [None] * (len(st) - len(en))))

LIM = 1.0

def prep(k):
    raw = f"voix_{k}.mp3"
    D = dur(raw)
    S = sil(raw)
    # segments parlés après chaque blanc ; on cherche le dernier blanc ≥ 0,35 s après lequel il reste < 1 s de parole
    best = None
    for i, (a, b) in enumerate(S):
        if b is None or b - a < 0.35:
            continue
        speech = 0.0
        t = b
        for (a2, b2) in S[i + 1:]:
            speech += max(0, a2 - t); t = b2 if b2 is not None else D
        speech += max(0, D - t)
        if speech < LIM and speech > 0.15:
            best = (a, b, round(speech, 2))
            break
    res = {"cle": k, "brut_s": round(D, 2), "derniers_blancs": [(round(a, 2), round(b, 2) if b else None) for a, b in S[-4:]]}
    if best is None:
        res["erreur"] = "pas de phrase sacrifiée isolée trouvée"
        print(json.dumps(res, ensure_ascii=False)); return res
    cut = best[0] + min(0.3, (best[1] - best[0]) / 2)   # dans le blanc : la voix finit sur un silence
    res["coupe_s"] = round(cut, 3); res["sacrifiee_s"] = best[2]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-t", str(cut), "-c:a", "libmp3lame", "-q:a", "2", f"cut_{k}.mp3"], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"cut_{k}.mp3", "-af",
                    "silenceremove=stop_periods=-1:stop_duration=0.25:stop_threshold=-35dB:stop_silence=0.22,atempo=1.1",
                    f"voix_{k}3.mp3"], check=True)
    subprocess.run(["rm", "-f", f"cut_{k}.mp3"])
    res["voix3_s"] = round(dur(f"voix_{k}3.mp3"), 3)
    res["tail_db"] = round(ac.tail_db(f"voix_{k}3.mp3"), 1)
    print(json.dumps(res, ensure_ascii=False))
    return res

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0].startswith("--lim="):
        LIM = float(args.pop(0)[6:])
    for k in args:
        prep(k)

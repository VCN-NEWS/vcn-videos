"""Contrôles bloquants avant brouillon (PIPELINE.md) : python3 controles.py <clé_v3> <vidéo_finale> [voix_brute_avec_ciao]
Durée ≥ 70 s, narration entière (voice_cut_in_video), aucune phrase répétée, phrase sacrifiée absente,
fin de voix sur un silence, synchro > 95 %, volume ≈ -16 dB, débit syllabique (mots avalés)."""
import sys, re, subprocess, json
import numpy as np
import audiocheck as ac
import videos

VOW = re.compile(r"[aeiouyàâäéèêëîïôöùûüœæ]+", re.I)


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)


def mean_volume(f):
    out = subprocess.run(["ffmpeg", "-i", f, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.search(r"mean_volume: (-?[\d.]+)", out).group(1))


def active(a, t, w=0.12):
    i, j = int(max(0, t - w) * ac.SR), int((t + w) * ac.SR)
    x = a[i:j]
    return len(x) and 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9) > -38


def repeats(voice, win=2.0, step=1.0, guard=3.0, thr=0.82):
    """Cherche un passage de 2 s qui se retrouve ailleurs dans la voix (phrase dite deux fois)."""
    F = ac.feats(voice)
    Fn = F / (np.linalg.norm(F, axis=1, keepdims=True) + 1e-9)
    L = int(win * 100)
    worst = (0, 0, 0)
    for s in np.arange(0, len(voice) / ac.SR - win, step):
        i = int(s * 100)
        A = Fn[i:i + L]
        best = -1
        for j in range(0, len(Fn) - L, 5):
            if abs(j - i) < guard * 100:
                continue
            c = float(np.mean(np.sum(A * Fn[j:j + L], 1)))
            if c > best:
                best, bj = c, j
        if best > worst[0]:
            worst = (best, s, bj / 100)
    return worst[0] < thr, worst


def main(key, video, raw=None):
    v = videos.VIDEOS[key]()
    voice_f = f"{videos.D}/voix_{key}.mp3"
    voice = ac.load(voice_f)
    res = {}
    d = dur(video)
    res["duree_s"] = round(d, 2)
    res["duree_ok"] = d >= 70
    cut = ac.voice_cut_in_video(video, voice_f, v.lead)
    res["voice_cut_in_video"] = cut
    tdb = ac.tail_db(voice_f)
    res["fin_voix_tail_db"] = round(tdb, 1)
    res["fin_silence_ok"] = tdb < -40
    ok_rep, worst = repeats(voice)
    res["phrase_repetee"] = {"ok": ok_rep, "similarite_max": round(worst[0], 2), "a": round(worst[1], 1), "b": round(worst[2], 1)}
    if raw:  # « Allez, ciao » = dernier segment parlé du MP3 brut ; il ne doit pas se retrouver dans la vidéo
        r = ac.load(raw)
        ciao = r[-int(0.9 * ac.SR):]
        tail = ac.load(video, ss=max(0, d - 6))
        sim, pos = ac.best_match(ciao, tail)
        res["phrase_sacrifiee"] = {"similarite": round(sim, 2), "absente": sim < 0.5}
    # synchro : chaque mot affiché doit tomber pendant que la voix parle
    words = [w for g in v.groups for w in g]
    vid_audio = voice
    hit = sum(1 for w in words if active(vid_audio, (w[1] + w[2]) / 2 - v.lead))
    res["synchro_pct"] = round(100 * hit / max(1, len(words)), 1)
    res["synchro_ok"] = res["synchro_pct"] > 95
    mv = mean_volume(video)
    res["volume_moyen_db"] = mv
    res["volume_ok"] = -18.5 <= mv <= -13.5
    # débit syllabique par phrase (mots avalés = phrase anormalement rapide)
    import scripts
    base = key[:-1]
    sents = v.sent
    rates = []
    for i, s in enumerate(sents):
        a, b = v.st[i]
        rates.append(len(VOW.findall(s)) / max(0.2, (b - a) * 1.1))
    med = float(np.median(rates))
    fast = [(i, sents[i][:40], round(r / med, 2)) for i, r in enumerate(rates) if r > 1.25 * med and len(sents[i]) > 12]
    res["debit_median_syll_s"] = round(med, 2)
    res["phrases_trop_rapides"] = fast
    res["TOUT_OK"] = bool(res["duree_ok"] and cut is None and res["fin_silence_ok"] and ok_rep and res["synchro_ok"]
                          and res["volume_ok"] and res.get("phrase_sacrifiee", {"absente": True})["absente"])
    print(json.dumps(res, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    return res


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)

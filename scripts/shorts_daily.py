#!/usr/bin/env python3
"""Daily AI Shorts: fetch news -> Gemini script -> edge-tts -> Pexels visuals -> YouTube upload.
Single lightweight script; deps: edge-tts, requests. ffmpeg must be on PATH.
Env: GEMINI_API_KEY, PEXELS_API_KEY, YT_CLIENT_ID/SECRET/REFRESH_TOKEN, UPLOAD_MODE(yt|dry-run).
"""
import json, os, re, subprocess, sys, tempfile, datetime, pathlib, shutil
import requests

TMP = pathlib.Path(tempfile.mkdtemp(prefix="shorts_"))
OUT = pathlib.Path(os.getenv("AIYT_STORAGE_ROOT", "./data/shorts")); OUT.mkdir(parents=True, exist_ok=True)

def die(msg): print(f"[ERROR] {msg}", file=sys.stderr); sys.exit(1)

def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: die(f"cmd failed: {' '.join(cmd)}\n{r.stderr[-500:]}")
    return r.stdout

# 1) Fetch daily news via RSS (no API key needed)
def fetch_news():
    try:
        import xml.etree.ElementTree as ET
        url = "https://news.google.com/rss/search?q=AI+models+OR+AI+tools+OR+AI+image+generation&hl=en-US&gl=US&ceid=US:en"
        root = ET.fromstring(requests.get(url, timeout=30).text)
        items = []
        for it in root.iter("item"):
            t = (it.findtext("title") or "").strip()
            l = (it.findtext("link") or "").strip()
            if t: items.append(f"- {t} ({l})")
            if len(items) >= 8: break
        return "\n".join(items) or None
    except Exception as e:
        print(f"[warn] news fetch failed: {e}"); return None

# 2) Generate Hindi/Hinglish script with Gemini
def gen_script(news):
    key = os.getenv("GEMINI_API_KEY")
    prompt = (
        "Tum ek YouTube Shorts creator ho. In news headlines se ek 45-second (approx 110-130 Hindi words) "
        "engaging Hindi/Hinglish script banao. Format: ek hi paragraph, bina headings, bina emoji, conversational tone. "
        "End me ek hook line: 'Aur updates ke liye channel ko follow karo!'\n\nNews headlines:\n" + (news or "General latest AI news")
    )
    if not key:
        print("[warn] GEMINI_API_KEY missing, using fallback script")
        return ("Namaskar dosto! Aaj ki AI duniya me bahut kuch ho raha hai. "
                "Naye models, naye tools, aur image generation me crazy updates aa rahe hain. "
                "AI ab sirf future nahi, aaj ka reality hai. Aur updates ke liye channel ko follow karo!")
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}",
        json=body, timeout=60)
    if r.status_code != 200: die(f"Gemini API {r.status_code}: {r.text[:300]}")
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

# 3) Voiceover via edge-tts
def make_voiceover(text, wav):
    try: import edge_tts
    except ImportError: die("pip install edge-tts")
    async def run():
        import asyncio
        c = edge_tts.Communicate(text, voice="hi-IN-MadhurNeural", rate="+10%")
        await c.save(str(wav))
    import asyncio; asyncio.run(run())
    if not wav.exists() or wav.stat().st_size < 1000: die("edge-tts produced no audio")

# 4) Stock visuals via Pexels + ffmpeg assembly (9:16, 30s+ clips cut to VO length)
def fetch_visuals(query="artificial intelligence technology"):
    key = os.getenv("PEXELS_API_KEY")
    if not key:
        print("[warn] PEXELS_API_KEY missing, using color background")
        return None
    r = requests.get("https://api.pexels.com/videos/search", params={"query": query, "orientation": "portrait", "per_page": 8},
                     headers={"Authorization": key}, timeout=30)
    if r.status_code != 200: print(f"[warn] pexels {r.status_code}"); return None
    vids = r.json().get("videos", [])
    files = []
    for i, v in enumerate(vids[:4]):
        vf = sorted(v.get("video_files", []), key=lambda f: f.get("width", 0))
        src = vf[-1]["link"] if vf else None
        if not src: continue
        p = TMP / f"v{i}.mp4"
        try:
            with requests.get(src, stream=True, timeout=60) as resp:
                resp.raise_for_status()
                with open(p, "wb") as f:
                    for chunk in resp.iter_content(1 << 16): f.write(chunk)
            files.append(p)
        except Exception as e:
            print(f"[warn] download {i}: {e}")
    return files

def assemble(vo_wav, visuals, out):
    dur = float(sh(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(vo_wav)]).strip())
    n = max(1, len(visuals or []))
    seg = max(3.0, dur / n + 0.2)
    if not visuals:
        sh(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=0x101820:s=1080x1920:d=%f" % dur,
            "-i", str(vo_wav), "-shortest", "-c:v", "libx264", "-crf", "23", "-c:a", "aac", str(out)])
        return dur
    ins = []
    for i, v in enumerate(visuals):
        ins += ["-i", str(v)]
    fc = "".join(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[t{i}];" for i in range(n))
    concat = "".join(f"[t{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vc];"
    sh(["ffmpeg", "-y", *ins, "-i", str(vo_wav), "-filter_complex",
        fc + concat + f"[vc]trim=duration={dur},setpts=PTS-STARTPTS[v]",
        "-map", "[v]", "-map", f"{n}:a", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "128k", str(out)])
    return dur

# 5) Upload via YouTube Data API v3 (refresh token flow, no google libs needed)
def upload_yt(video, title):
    cid, cs, rt = (os.getenv(k, "") for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))
    if not all([cid, cs, rt]): die("YouTube creds missing (YT_CLIENT_ID/SECRET/REFRESH_TOKEN)")
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": cid, "client_secret": cs, "refresh_token": rt, "grant_type": "refresh_token"}, timeout=30)
    if r.status_code != 200: die(f"token refresh failed: {r.text[:200]}")
    at = r.json()["access_token"]
    meta = {"snippet": {"title": title[:100], "description": "Daily AI news in 60s! #shorts #ai #tech",
                        "tags": ["ai", "tech", "shorts"], "categoryId": "28"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}
    body = (b"--=BOUND==\r\nContent-Type: application/json\r\n\r\n" +
            json.dumps(meta).encode() +
            b"\r\n--=BOUND==\r\nContent-Type: video/mp4\r\n\r\n" +
            video.read_bytes() + b"\r\n--=BOUND==--\r\n")
    r = requests.post("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=multipart&part=snippet,status",
                      headers={"Authorization": f"Bearer {at}", "Content-Type": "multipart/related; boundary==BOUND=="},
                      data=body, timeout=600)
    if r.status_code not in (200, 201): die(f"upload failed {r.status_code}: {r.text[:300]}")
    return r.json().get("id", "?")

def main():
    date = datetime.date.today().isoformat()
    title = f"AI Update {date} #shorts"
    print(f"[1/5] Fetching news..."); news = fetch_news()
    print(f"[2/5] Generating script..."); script = gen_script(news)
    (OUT / f"script_{date}.txt").write_text(script, encoding="utf-8")
    print(f"[3/5] Generating voiceover...")
    vo = TMP / "vo.mp3"; make_voiceover(script, vo)
    print(f"[4/5] Assembling video...")
    visuals = fetch_visuals()
    out = OUT / f"shorts_{date}.mp4"
    assemble(vo, visuals, out)
    print(f"[5/5] Uploading...")
    if os.getenv("UPLOAD_MODE", "dry-run") == "yt":
        vid = upload_yt(out, title)
        print(f"UPLOADED: https://youtube.com/shorts/{vid}")
    else:
        print(f"DRY-RUN: kept {out} ({out.stat().st_size/1e6:.1f} MB). Set UPLOAD_MODE=yt to publish.")
    shutil.rmtree(TMP, ignore_errors=True)

if __name__ == "__main__":
    main()

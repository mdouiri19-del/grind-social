"""Push one day's media to GitHub and write the manifest Make.com reads.

Usage: python3 tools/publish.py YYYY-MM-DD
Expects in queue/YYYY-MM-DD/: reel.mp4, reel_caption.txt, post_01.jpg..post_06.jpg, post_caption.txt, meta.json (pillars, hooks)
Step 1 commits + pushes media, step 2 writes manifest.json with URLs pinned to that commit, commits + pushes.
"""
import json, os, subprocess, sys

REPO = "mdouiri19-del/grind-social"
TRAILER = "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

def sh(*a):
    return subprocess.run(a, check=True, capture_output=True, text=True).stdout.strip()

def main(day):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    d = f"queue/{day}"
    need = ["reel.mp4", "reel_caption.txt", "post_caption.txt"] + [f"post_0{i}.jpg" for i in range(1, 7)]
    missing = [f for f in need if not os.path.exists(f"{d}/{f}")]
    if missing:
        sys.exit(f"missing: {missing}")
    if os.path.getsize(f"{d}/reel.mp4") > 19_000_000:
        sys.exit("reel.mp4 over 19 MB, re-encode smaller")
    sh("git", "config", "user.name", "GRIND.")
    sh("git", "config", "user.email", "bot@grindstudent.com")
    sh("git", "pull", "--rebase", "-q", "origin", "main")
    sh("git", "add", d)
    if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode != 0:
        sh("git", "commit", "-qm", f"Media {day}{TRAILER}")
    sh("git", "push", "-q", "origin", "HEAD:main")
    sha = sh("git", "rev-parse", "HEAD")
    raw = f"https://raw.githubusercontent.com/{REPO}/{sha}/{d}/"
    cdn = f"https://cdn.jsdelivr.net/gh/{REPO}@{sha}/{d}/"
    meta = json.load(open(f"{d}/meta.json")) if os.path.exists(f"{d}/meta.json") else {}
    m = {
        "date": day,
        "reel_url": cdn + "reel.mp4",
        "reel_url_raw": raw + "reel.mp4",
        "reel_caption": open(f"{d}/reel_caption.txt").read().strip(),
        "post_caption": open(f"{d}/post_caption.txt").read().strip(),
        **meta,
    }
    m.setdefault("cover_ms", 1900)
    if os.path.exists(f"{d}/cover.jpg"):
        m["cover_url"] = cdn + "cover.jpg"
        m["cover_url_raw"] = raw + "cover.jpg"
    if os.path.exists(f"{d}/linkedin.txt"):
        m["linkedin_text"] = open(f"{d}/linkedin.txt").read().strip()
        img = "linkedin.jpg" if os.path.exists(f"{d}/linkedin.jpg") else "post_01.jpg"
        m["linkedin_image_url"] = raw + img
    if os.path.exists(f"{d}/cta.jpg"):
        m["cta_url"] = cdn + "cta.jpg"
        m["cta_url_raw"] = raw + "cta.jpg"
        m["cta_caption"] = open(f"{d}/cta_caption.txt").read().strip() if os.path.exists(f"{d}/cta_caption.txt") else ""
    for i in range(1, 7):
        m[f"post_{i}"] = cdn + f"post_0{i}.jpg"
        m[f"post_{i}_raw"] = raw + f"post_0{i}.jpg"
    json.dump(m, open(f"{d}/manifest.json", "w"), indent=1, ensure_ascii=False)
    sh("git", "add", f"{d}/manifest.json")
    sh("git", "commit", "-qm", f"Manifest {day}{TRAILER}")
    sh("git", "push", "-q", "origin", "HEAD:main")
    print(json.dumps(m, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main(sys.argv[1])

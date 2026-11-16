"""Generate assets/top-langs.svg from the owner's public, non-fork repos."""
import json, os, sys, urllib.request
from html import escape

USER = os.environ.get("GH_USER", "Salateek2")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
TOP_N = 8
COLORS = {
    "Java": "#ED8B00", "C#": "#9B4F96", "GDScript": "#478CBF", "JavaScript": "#F7DF1E",
    "TypeScript": "#3178C6", "HTML": "#E34C26", "CSS": "#663399", "Kotlin": "#A97BFF",
    "Python": "#3776AB", "ShaderLab": "#222C37", "HLSL": "#AACE60", "C++": "#F34B7D",
}
FALLBACK = "#9CA3AF"
SKIP = {"ShaderLab", "HLSL", "Batchfile", "Shell"}  # engine/build noise, not "languages I write"


def api(path):
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("Accept", "application/vnd.github+json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect():
    totals, page = {}, 1
    while True:
        repos = api(f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        if not repos:
            break
        for r in repos:
            if r.get("fork") or r.get("private"):
                continue
            for lang, n in api(f"/repos/{USER}/{r['name']}/languages").items():
                if lang not in SKIP:
                    totals[lang] = totals.get(lang, 0) + n
        page += 1
    return totals


def render(totals):
    items = sorted(totals.items(), key=lambda kv: -kv[1])[:TOP_N]
    total = sum(n for _, n in items) or 1
    row_h, top = 30, 56
    h = top + row_h * max(len(items), 1) + 16
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="420" height="{h}" viewBox="0 0 420 {h}" role="img" aria-label="Top languages">',
           '<style>text{font-family:Segoe UI,Helvetica,Arial,sans-serif;fill:#e5e7eb}.t{font-size:16px;font-weight:600}.l{font-size:13px}.p{font-size:12px;fill:#9ca3af}</style>',
           f'<rect width="420" height="{h}" rx="10" fill="#0d1117" stroke="#30363d"/>',
           '<text x="20" y="32" class="t">Top languages</text>']
    if not items:
        out.append('<text x="20" y="70" class="l">No public repos with code yet</text>')
    for i, (lang, n) in enumerate(items):
        y = top + i * row_h
        pct = n * 100 / total
        out.append(f'<text x="20" y="{y + 11}" class="l">{escape(lang)}</text>')
        out.append(f'<rect x="120" y="{y}" width="220" height="10" rx="5" fill="#21262d"/>')
        out.append(f'<rect x="120" y="{y}" width="{max(pct * 2.2, 4):.1f}" height="10" rx="5" fill="{COLORS.get(lang, FALLBACK)}"/>')
        out.append(f'<text x="352" y="{y + 10}" class="p">{pct:.1f}%</text>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    data = collect()
    os.makedirs("assets", exist_ok=True)
    with open("assets/top-langs.svg", "w", encoding="utf-8") as f:
        f.write(render(data))
    print("Wrote assets/top-langs.svg:", data, file=sys.stderr)

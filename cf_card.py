#!/usr/bin/env python3
"""Genera assets/cf-card.svg con el rango y rating actuales de Codeforces.

Uso:
    CF_HANDLE=Hery python .github/scripts/cf_card.py

Si la API falla, NO toca el archivo existente (la tarjeta anterior se queda).
Solo usa la libreria estandar de Python.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from xml.sax.saxutils import escape

HANDLE = os.environ.get("CF_HANDLE", "Hery")
OUT = os.environ.get("CF_OUT", "assets/cf-card.svg")
MOCK = os.environ.get("CF_MOCK")  # ruta a un JSON, solo para pruebas

# (nombre en la API, minimo de rating, etiqueta, color sobre fondo oscuro, grado)
RANKS = [
    ("newbie", 0, "Newbie", "#9ca3af", "GRADO 4"),
    ("pupil", 1200, "Pupil", "#22c55e", "GRADO 3"),
    ("specialist", 1400, "Specialist", "#06b6d4", "GRADO 2"),
    ("expert", 1600, "Expert", "#60a5fa", "GRADO 1"),
    ("candidate master", 1900, "Candidate Master", "#c084fc", "GRADO ESPECIAL"),
    ("master", 2100, "Master", "#fb923c", "GRADO ESPECIAL"),
    ("international master", 2300, "International Master", "#fb923c", "GRADO ESPECIAL"),
    ("grandmaster", 2400, "Grandmaster", "#f87171", "GRADO ESPECIAL"),
    ("international grandmaster", 2600, "International Grandmaster", "#f87171", "GRADO ESPECIAL"),
    ("legendary grandmaster", 3000, "Legendary Grandmaster", "#f87171", "GRADO ESPECIAL"),
]


def rank_index(name):
    name = (name or "").strip().lower()
    for i, r in enumerate(RANKS):
        if r[0] == name:
            return i
    return 0


def fetch(handle):
    if MOCK:
        with open(MOCK, encoding="utf-8") as f:
            data = json.load(f)
    else:
        url = f"https://codeforces.com/api/user.info?handles={handle}"
        req = urllib.request.Request(url, headers={"User-Agent": "profile-readme-card/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
    if data.get("status") != "OK" or not data.get("result"):
        raise RuntimeError(f"API respondio: {data.get('comment', data.get('status'))}")
    return data["result"][0]


def render(info):
    handle = info.get("handle", HANDLE)
    rating = info.get("rating")
    max_rating = info.get("maxRating")
    idx = rank_index(info.get("rank"))
    _, lo, label, color, grade = RANKS[idx]
    max_idx = rank_index(info.get("maxRank"))
    max_label = RANKS[max_idx][2]

    if idx + 1 < len(RANKS):
        hi = RANKS[idx + 1][1]
        next_label = RANKS[idx + 1][2]
        if rating is None:
            progress = 0.0
        else:
            progress = max(0.0, min(1.0, (rating - lo) / float(hi - lo)))
        remaining = None if rating is None else max(0, hi - rating)
    else:
        next_label = None
        progress = 1.0
        remaining = None

    bar_w = 560
    fill_w = round(bar_w * progress, 1)
    rating_txt = str(rating) if rating is not None else "—"
    max_txt = str(max_rating) if max_rating is not None else "—"

    if next_label and remaining is not None:
        goal = f"FALTAN {remaining} PUNTOS PARA {next_label.upper()}"
    elif next_label:
        goal = f"SIGUIENTE: {next_label.upper()}"
    else:
        goal = "RANGO MAXIMO ALCANZADO"

    h = escape(handle)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 190" width="100%" role="img" aria-label="Codeforces: {h}, {escape(label)}, rating {escape(rating_txt)}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0b0a1f"/>
      <stop offset="1" stop-color="#171040"/>
    </linearGradient>
    <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{color}"/>
      <stop offset="1" stop-color="#a78bfa"/>
    </linearGradient>
  </defs>
  <style>
    .mono {{ font-family: 'Courier New', Consolas, monospace; }}
    .sans {{ font-family: 'Impact', 'Trebuchet MS', 'Segoe UI', sans-serif; }}
    .fill {{ transform-box: fill-box; transform-origin: left center; transform: scaleX(0); animation: grow 1.6s cubic-bezier(.2,.8,.2,1) forwards; }}
    @keyframes grow {{ to {{ transform: scaleX(1); }} }}
    .pulse {{ animation: pulse 2.4s ease-in-out infinite; }}
    @keyframes pulse {{ 0%,100% {{ opacity: .55; }} 50% {{ opacity: 1; }} }}
  </style>
  <rect width="900" height="190" rx="14" fill="url(#bg)"/>
  <rect x="1" y="1" width="898" height="188" rx="13" fill="none" stroke="{color}" stroke-opacity=".6" stroke-width="2"/>

  <text class="mono" x="30" y="36" font-size="14" font-weight="700" letter-spacing="3" fill="#60a5fa">▌CODEFORCES · SINCRONIZADO</text>
  <text class="mono" x="870" y="36" text-anchor="end" font-size="12" letter-spacing="2" fill="#6b7280">{escape(grade)}</text>
  <line x1="30" y1="50" x2="870" y2="50" stroke="#7c3aed" stroke-opacity=".45"/>

  <text class="sans" x="30" y="98" font-size="40" letter-spacing="4" fill="{color}">{h}</text>
  <text class="mono" x="30" y="122" font-size="15" font-weight="700" fill="{color}">{escape(label.upper())}</text>

  <text class="mono" x="620" y="72" font-size="12" letter-spacing="2" fill="#9ca3af">RATING</text>
  <text class="sans pulse" x="620" y="128" font-size="48" fill="#ffffff">{escape(rating_txt)}</text>
  <text class="mono" x="780" y="72" font-size="12" letter-spacing="2" fill="#9ca3af">MAXIMO</text>
  <text class="sans" x="780" y="124" font-size="34" fill="#fbbf24">{escape(max_txt)}</text>
  <text class="mono" x="780" y="142" font-size="11" fill="#9ca3af">{escape(max_label)}</text>

  <rect x="30" y="150" width="{bar_w}" height="12" rx="6" fill="#1b1648"/>
  <rect class="fill" x="30" y="150" width="{fill_w}" height="12" rx="6" fill="url(#bar)"/>
  <text class="mono" x="30" y="180" font-size="11" letter-spacing="1" fill="#a78bfa">{escape(goal)}</text>
</svg>
'''
    return svg


def main():
    try:
        info = fetch(HANDLE)
    except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, OSError) as exc:
        print(f"[cf_card] No se pudo consultar Codeforces: {exc}", file=sys.stderr)
        print("[cf_card] Se conserva la tarjeta anterior.", file=sys.stderr)
        return 0
    svg = render(info)
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[cf_card] {info.get('handle')} -> {info.get('rank')} ({info.get('rating')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

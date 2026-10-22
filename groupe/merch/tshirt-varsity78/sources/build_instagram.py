"""Visuels Instagram (1080 × 1350) du t-shirt Varsity 78, face et dos, noir et blanc.

Le t-shirt est dessiné en centimètres (oversize, taille L) et les marquages sont
les fichiers d'impression eux-mêmes, posés à leur taille réelle.
Usage : python3 build_instagram.py   (lance node render_png.js pour chaque image)
"""
import os
import re
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PRINTS = os.path.join(HERE, "..", "impression")
OUT = os.path.join(HERE, "..", "instagram")
FONTS = os.path.join(HERE, "fonts")

W, H = 1080, 1350
BG = "#F1EADB"
INK_TEXT = "#1F3D22"

# Silhouette oversize à plat, en cm (viewBox 0 0 100 90).
BODY_FRONT = ("M41 4 Q50 13.5 59 4 L82 9 C88 13 93 21 96 30 L88 37 L80 31 L80 83 "
              "Q50 85.5 20 83 L20 31 L12 37 L4 30 C7 21 12 13 18 9 Z")
BODY_BACK = ("M41 4 Q50 7 59 4 L82 9 C88 13 93 21 96 30 L88 37 L80 31 L80 83 "
             "Q50 85.5 20 83 L20 31 L12 37 L4 30 C7 21 12 13 18 9 Z")

FABRICS = {
    "noir": {"fill": "#1C1C1C", "rib": "#262626", "inside": "#0E0E0E", "seam": "#303030",
             "shade": "#000000", "shade_op": 0.55, "light": "#FFFFFF", "light_op": 0.025,
             "noise_op": 0.10, "ink": "creme", "label": "Noir"},
    "blanc": {"fill": "#FBFAF6", "rib": "#F1EFE9", "inside": "#E6E3DA", "seam": "#D8D4C8",
              "shade": "#8A8370", "shade_op": 0.30, "light": "#FFFFFF", "light_op": 0.0,
              "noise_op": 0.06, "ink": "vert", "label": "Blanc"},
}

# Placement des marquages sur le gabarit (cm)
FACE_POS = (57.0, 14.0)     # coin haut-gauche du logo de 8 cm, côté cœur
BACK_TOP = 13.5             # haut du visuel dos


def load_print(name):
    src = open(os.path.join(PRINTS, name), encoding="utf-8").read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src).group(1).split()]
    inner = re.search(r"(<g fill=.*</g>)", src, re.S).group(1)
    return vb, inner


def placed(name, x_cm, y_cm, width_cm=None):
    """Le fichier d'impression posé à taille réelle (1 mm = 0,1 cm du gabarit)."""
    vb, inner = load_print(name)
    w_cm = vb[2] / 10 if width_cm is None else width_cm
    h_cm = vb[3] * w_cm / vb[2]
    return (f'<svg x="{x_cm}" y="{y_cm}" width="{w_cm}" height="{h_cm}" '
            f'viewBox="{" ".join(str(v) for v in vb)}" overflow="visible">{inner}</svg>'), w_cm, h_cm


def tee_svg(fab, side):
    f = FABRICS[fab]
    body = BODY_FRONT if side == "face" else BODY_BACK
    ink = f["ink"]
    if side == "face":
        art, _, _ = placed(f"BS-varsity78_face-coeur_80mm_encre-{ink}.svg", *FACE_POS)
        neck_inside = '<path d="M41 4 Q50 7 59 4 Q50 13.5 41 4 Z" fill="{}"/>'.format(f["inside"])
        neck_rib = '<path d="M41 4 Q50 13.5 59 4" fill="none" stroke="{}" stroke-width="2.2"/>'.format(f["rib"])
        rib_line = '<path d="M42.2 4.6 Q50 12.3 57.8 4.6" fill="none" stroke="{}" stroke-width="0.12"/>'.format(f["seam"])
    else:
        art, w, _ = placed(f"BS-varsity78_dos_300mm_encre-{ink}.svg", 0, BACK_TOP)
        art = art.replace('x="0"', f'x="{50 - w / 2}"', 1)
        neck_inside = ""
        neck_rib = '<path d="M41 4 Q50 7 59 4" fill="none" stroke="{}" stroke-width="2.2"/>'.format(f["rib"])
        rib_line = '<path d="M42.2 4.9 Q50 7.6 57.8 4.9" fill="none" stroke="{}" stroke-width="0.12"/>'.format(f["seam"])
    s = f["seam"]
    return f"""
<svg viewBox="0 0 100 90" width="100%" height="100%" aria-hidden="true">
  <defs>
    <clipPath id="tee"><path d="{body}"/></clipPath>
    <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.6"/></filter>
    <filter id="softer" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="0.6"/></filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.4"/></filter>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="2.2" numOctaves="2" seed="7"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>
    <linearGradient id="sides" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0" stop-color="{f['shade']}" stop-opacity="{f['shade_op']}"/>
      <stop offset="0.22" stop-color="{f['shade']}" stop-opacity="0"/>
      <stop offset="0.78" stop-color="{f['shade']}" stop-opacity="0"/>
      <stop offset="1" stop-color="{f['shade']}" stop-opacity="{f['shade_op']}"/>
    </linearGradient>
  </defs>
  <path d="{body}" transform="translate(0.6 1.4)" fill="#5A4E35" opacity="0.28" filter="url(#shadow)"/>
  <path d="{body}" fill="{f['fill']}"/>
  {neck_inside}
  <g clip-path="url(#tee)">
    <rect x="0" y="0" width="100" height="90" fill="url(#sides)"/>
    <path d="M27 50 C33 58 36 70 34 84" fill="none" stroke="{f['shade']}" stroke-opacity="{f['shade_op'] * 0.5}" stroke-width="2.4" filter="url(#soft)"/>
    <path d="M72 46 C67 57 66 70 69 84" fill="none" stroke="{f['shade']}" stroke-opacity="{f['shade_op'] * 0.45}" stroke-width="2.2" filter="url(#soft)"/>
    <path d="M24 40 C30 46 32 52 33 58" fill="none" stroke="{f['light']}" stroke-opacity="{f['light_op'] * 2}" stroke-width="1.6" filter="url(#soft)"/>
    <path d="M10 33 C14 30 17 28 19 24" fill="none" stroke="{f['shade']}" stroke-opacity="{f['shade_op'] * 0.4}" stroke-width="1.2" filter="url(#soft)"/>
    <path d="M90 33 C86 30 83 28 81 24" fill="none" stroke="{f['shade']}" stroke-opacity="{f['shade_op'] * 0.4}" stroke-width="1.2" filter="url(#soft)"/>
    {art}
    <rect x="0" y="0" width="100" height="90" filter="url(#grain)" opacity="{f['noise_op']}" style="mix-blend-mode:overlay"/>
    <path d="M18 9 C19.5 16 20 24 20 31 M82 9 C80.5 16 80 24 80 31" fill="none" stroke="{s}" stroke-width="0.15"/>
    <path d="M5.6 31.6 L13.2 36.6 M94.4 31.6 L86.8 36.6" fill="none" stroke="{s}" stroke-width="0.12" stroke-dasharray="0.5 0.35"/>
    <path d="M20 81 Q50 83.4 80 81" fill="none" stroke="{s}" stroke-width="0.12" stroke-dasharray="0.5 0.35"/>
  </g>
  {neck_rib}
  {rib_line}
</svg>"""


def inset_svg(fab):
    f = FABRICS[fab]
    art, _, _ = placed(f"BS-varsity78_face-coeur_80mm_encre-{f['ink']}.svg", 1.5, 2.33)
    return f"""
<svg viewBox="0 0 11 11" width="100%" height="100%" aria-hidden="true">
  <defs><filter id="grain2" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="9" numOctaves="2" seed="3"/>
    <feColorMatrix type="saturate" values="0"/></filter>
    <clipPath id="disc"><circle cx="5.5" cy="5.5" r="5.5"/></clipPath></defs>
  <g clip-path="url(#disc)">
    <rect width="11" height="11" fill="{f['fill']}"/>
    {art}
    <rect width="11" height="11" filter="url(#grain2)" opacity="{f['noise_op']}" style="mix-blend-mode:overlay"/>
  </g>
</svg>"""


def page(fab, side):
    f = FABRICS[fab]
    inset = ""
    if side == "face":
        inset = f"""
  <div style="position:absolute;right:70px;bottom:205px;width:250px;height:250px;border-radius:50%;
              box-shadow:0 0 0 6px {BG}, 0 0 0 8px {INK_TEXT};overflow:hidden">{inset_svg(fab)}</div>
  <div style="position:absolute;right:70px;bottom:168px;width:250px;text-align:center;
              font:600 17px/1 'Oswald';letter-spacing:.18em;color:{INK_TEXT}">CÔTÉ CŒUR · 8 CM</div>"""
    side_label = "FACE" if side == "face" else "DOS"
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
@font-face {{ font-family: 'Graduate'; src: url('file://{FONTS}/Graduate-Regular.ttf'); }}
@font-face {{ font-family: 'Oswald'; font-weight: 600; src: url('file://{FONTS}/Oswald-SemiBold.ttf'); }}
html, body {{ margin: 0; }}
body {{ width: {W}px; height: {H}px; background: {BG}; position: relative; overflow: hidden; color: {INK_TEXT}; }}
</style></head><body>
  <div style="position:absolute;left:70px;top:62px;display:flex;flex-direction:column;gap:12px">
    <div style="font:44px/1 'Graduate'">BODYSTART</div>
    <div style="font:600 19px/1 'Oswald';letter-spacing:.3em">ATHLETIC CLUB · 78</div>
  </div>
  <div style="position:absolute;right:70px;top:66px;font:600 19px/1 'Oswald';letter-spacing:.3em;
              border:2px solid {INK_TEXT};padding:10px 16px">{side_label}</div>
  <div style="position:absolute;left:50px;top:205px;width:980px;height:882px">{tee_svg(fab, side)}</div>
  {inset}
  <div style="position:absolute;left:70px;right:70px;bottom:62px;display:flex;justify-content:space-between;
              align-items:flex-end;font:600 19px/1.5 'Oswald';letter-spacing:.14em">
    <div>T-SHIRT OVERSIZE 250 G<br><span style="font-family:'Graduate';font-weight:400;font-size:30px;letter-spacing:.02em">{f['label'].upper()}</span></div>
    <div style="text-align:right">BODYSTART NUTRITION<br>COIGNIÈRES</div>
  </div>
</body></html>"""


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp()
    for fab in ("noir", "blanc"):
        for side in ("face", "dos"):
            html = os.path.join(tmp, f"{fab}-{side}.html")
            with open(html, "w", encoding="utf-8") as fh:
                fh.write(page(fab, side))
            out = os.path.join(OUT, f"BS-varsity78_instagram_{fab}_{side}.png")
            subprocess.run(["node", os.path.join(HERE, "render_png.js"), html, out, str(W), str(H)], check=True)
            print(out)


if __name__ == "__main__":
    main()

"""Génère les fichiers d'impression SVG (textes vectorisés) du t-shirt Varsity 78.

Unités : millimètres. Sortie : ../impression/*.svg et ../logo/*.svg
Usage : python3 build_prints.py
"""
import json
import math
import os

from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PRINT = os.path.join(HERE, "..", "impression")
OUT_LOGO = os.path.join(HERE, "..", "logo")

INKS = {
    "creme": ("#F1EADB", "crème #F1EADB, pour t-shirt noir"),
    "vert": ("#3B7A3F", "vert BodyStart #3B7A3F, pour t-shirt blanc"),
}

GRADUATE = TTFont(os.path.join(HERE, "fonts", "Graduate-Regular.ttf"))
OSWALD = TTFont(os.path.join(HERE, "fonts", "Oswald-SemiBold.ttf"))
LOGO = json.load(open(os.path.join(HERE, "logo_simple.json")))

BACK_WIDTH = 300.0   # mm, largeur du visuel dos
BACK_MAX_H = 350.0   # mm, hauteur maxi autorisée


def fmt(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


class Shape:
    """Un ensemble de tracés en mm, avec sa boîte englobante."""

    def __init__(self):
        self.paths = []          # (d, fill_rule)
        self.bounds = None       # (xmin, ymin, xmax, ymax)

    def add(self, d, bounds, rule="nonzero"):
        self.paths.append((d, rule))
        if bounds is None:
            return
        if self.bounds is None:
            self.bounds = bounds
        else:
            a = self.bounds
            self.bounds = (min(a[0], bounds[0]), min(a[1], bounds[1]),
                           max(a[2], bounds[2]), max(a[3], bounds[3]))


def glyph_outline(font, ch, transform, accent_lift=0):
    """Contour d'un caractère, transformé. Renvoie (d, bounds, advance_units).

    accent_lift (unités de fonte) remonte les accents des lettres composées,
    pour garder un jour d'au moins 1,5 mm entre l'accent et la lettre en flocage.
    """
    cmap = font.getBestCmap()
    gname = cmap[ord(ch)]
    gs = font.getGlyphSet()
    svg = SVGPathPen(gs, ntos=fmt)
    bp = BoundsPen(gs)
    glyph = font["glyf"][gname]
    if accent_lift and glyph.isComposite():
        for i, comp in enumerate(glyph.components):
            t = transform.translate(comp.x, comp.y + (accent_lift if i else 0))
            gs[comp.glyphName].draw(TransformPen(svg, t))
            gs[comp.glyphName].draw(TransformPen(bp, t))
    else:
        gs[gname].draw(TransformPen(svg, transform))
        gs[gname].draw(TransformPen(bp, transform))
    return svg.getCommands(), bp.bounds, font["hmtx"][gname][0]


def advance(font, ch):
    return font["hmtx"][font.getBestCmap()[ord(ch)]][0]


def text_width(font, text, size, tracking_em):
    upm = font["head"].unitsPerEm
    w = sum(advance(font, c) for c in text) * size / upm
    return w + tracking_em * size * (len(text) - 1)


def straight_text(shape, font, text, size, tracking_em, cx, baseline, accent_lift=0):
    """Texte centré horizontalement sur cx, posé sur la ligne de base y = baseline."""
    upm = font["head"].unitsPerEm
    k = size / upm
    x = cx - text_width(font, text, size, tracking_em) / 2
    for c in text:
        if c != " ":
            t = Transform().translate(x, baseline).scale(k, -k)
            d, b, _ = glyph_outline(font, c, t, accent_lift)
            shape.add(d, b)
        x += advance(font, c) * k + tracking_em * size


def quad_point(p0, p1, p2, t):
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
    dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
    dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
    return x, y, math.atan2(dy, dx)


def arc_text(shape, font, text, size, tracking_em, p0, p1, p2):
    """Texte centré le long d'une courbe quadratique (comme textPath, startOffset 50 %)."""
    n = 4000
    pts = [quad_point(p0, p1, p2, i / n) for i in range(n + 1)]
    lens = [0.0]
    for i in range(1, n + 1):
        lens.append(lens[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
    total = lens[-1]

    def at(s):
        lo, hi = 0, n
        while lo < hi:
            mid = (lo + hi) // 2
            if lens[mid] < s:
                lo = mid + 1
            else:
                hi = mid
        return pts[lo]

    upm = font["head"].unitsPerEm
    k = size / upm
    s = (total - text_width(font, text, size, tracking_em)) / 2
    for c in text:
        a = advance(font, c) * k
        x, y, ang = at(s + a / 2)
        t = Transform().translate(x, y).rotate(ang).translate(-a / 2, 0).scale(k, -k)
        d, b, _ = glyph_outline(font, c, t)
        shape.add(d, b)
        s += a + tracking_em * size


def logo(shape, width, x, y):
    """Logo simplifié (tracé potrace en px), mis à l'échelle à `width` mm, coin haut-gauche (x, y)."""
    k = width / LOGO["w"]
    h = LOGO["h"] * k
    d = LOGO["d"]
    # Le tracé est en px ; on l'enveloppe dans un transform plutôt que de réécrire les coordonnées.
    shape.paths.append((f'<path transform="translate({fmt(x)} {fmt(y)}) scale({k:.6f})" fill-rule="evenodd" d="{d}"/>', "raw"))
    b = (x, y, x + width, y + h)
    shape.bounds = b if shape.bounds is None else (
        min(shape.bounds[0], b[0]), min(shape.bounds[1], b[1]),
        max(shape.bounds[2], b[2]), max(shape.bounds[3], b[3]))
    return h


def write_svg(shape, path, color, title, desc):
    x0, y0, x1, y1 = shape.bounds
    w, h = x1 - x0, y1 - y0
    body = []
    for d, rule in shape.paths:
        if rule == "raw":
            body.append(d)
        else:
            body.append(f'<path fill-rule="{rule}" d="{d}"/>')
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(w)}mm" height="{fmt(h)}mm" '
        f'viewBox="{fmt(x0)} {fmt(y0)} {fmt(w)} {fmt(h)}">\n'
        f"<title>{title}</title>\n<desc>{desc}</desc>\n"
        f'<g fill="{color}">\n' + "\n".join(body) + "\n</g>\n</svg>\n"
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return w, h


def build_back():
    cx = BACK_WIDTH / 2
    # 1. « BODYSTART » en arc : corps ajusté pour que l'arc occupe toute la largeur
    sag = 30.0
    y_ends = 70.0
    p0, p2 = (-20.0, y_ends + 8), (BACK_WIDTH + 20.0, y_ends + 8)
    p1 = (cx, y_ends - 2 * sag)
    lo, hi = 30.0, 70.0
    for _ in range(30):
        size_arc = (lo + hi) / 2
        s = Shape()
        arc_text(s, GRADUATE, "BODYSTART", size_arc, 0.02, p0, p1, p2)
        if s.bounds[2] - s.bounds[0] > BACK_WIDTH:
            hi = size_arc
        else:
            lo = size_arc
    s = Shape()
    arc_text(s, GRADUATE, "BODYSTART", lo, 0.02, p0, p1, p2)
    # recale l'arc pour que son bord gauche soit à x = 0
    dx = -s.bounds[0]
    s = Shape()
    arc_text(s, GRADUATE, "BODYSTART", lo, 0.02,
             (p0[0] + dx, p0[1]), (p1[0] + dx, p1[1]), (p2[0] + dx, p2[1]))
    print(f"arc : corps {lo:.1f} mm")
    y = s.bounds[3]
    # 2. ATHLETIC CLUB
    y += 13.0
    size_ac = 21.0
    cap_ac = 0.81 * size_ac
    straight_text(s, OSWALD, "ATHLETIC CLUB", size_ac, 0.22, cx, y + cap_ac)
    y += cap_ac
    # 3. Logo
    y += 15.0
    lw = 138.0
    lh = logo(s, lw, cx - lw / 2, y)
    y += lh
    # 4. 78
    y += 13.0
    size_78 = 98.0
    cap_78 = 0.75 * size_78
    straight_text(s, GRADUATE, "78", size_78, 0.0, cx, y + cap_78)
    y += cap_78
    # 5. COIGNIÈRES
    y += 15.0
    size_c = 21.0
    cap_c = 0.81 * size_c
    straight_text(s, OSWALD, "COIGNIÈRES", size_c, 0.26, cx, y + cap_c, accent_lift=70)
    return s


def build_face():
    s = Shape()
    logo(s, 80.0, 0, 0)
    return s


def main():
    os.makedirs(OUT_PRINT, exist_ok=True)
    os.makedirs(OUT_LOGO, exist_ok=True)
    back = build_back()
    bw = back.bounds[2] - back.bounds[0]
    bh = back.bounds[3] - back.bounds[1]
    assert bw <= BACK_WIDTH + 0.01, f"dos trop large : {bw:.1f} mm"
    assert bh <= BACK_MAX_H, f"dos trop haut : {bh:.1f} mm"
    face = build_face()
    report = []
    for key, (color, label) in INKS.items():
        w, h = write_svg(
            face, os.path.join(OUT_PRINT, f"BS-varsity78_face-coeur_80mm_encre-{key}.svg"), color,
            "BodyStart Varsity 78, face côté cœur",
            f"Logo simplifié. Taille réelle {w_h(face)}. Flocage 1 couleur : {label}.")
        report.append(("face", key, w, h))
        w, h = write_svg(
            back, os.path.join(OUT_PRINT, f"BS-varsity78_dos_300mm_encre-{key}.svg"), color,
            "BodyStart Varsity 78, dos",
            f"Textes vectorisés. Taille réelle {w_h(back)}. Flocage 1 couleur : {label}.")
        report.append(("dos", key, w, h))
    for key, color in (("noir", "#141414"), ("vert", "#3B7A3F"), ("creme", "#F1EADB"), ("blanc", "#FFFFFF")):
        write_svg(face, os.path.join(OUT_LOGO, f"logo-bodystart-simplifie_{key}.svg"), color,
                  "Logo BodyStart simplifié", "Version 1 couleur pour flocage et petits formats (≥ 6 cm de large).")
    for r in report:
        print(f"{r[0]:5} {r[1]:6} {r[2]:.1f} x {r[3]:.1f} mm")


def w_h(shape):
    b = shape.bounds
    return f"{b[2] - b[0]:.0f} × {b[3] - b[1]:.0f} mm"


if __name__ == "__main__":
    main()

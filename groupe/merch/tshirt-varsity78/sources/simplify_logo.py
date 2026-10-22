"""Logo BodyStart simplifié pour le flocage (1 couleur, traits et jours >= 1,8 mm à 8 cm de large).

Part du logo 1 couleur d'origine (tracé potrace très détaillé, filets de 0,2 mm),
le rastérise à 2800 px de large (2800 px = 80 mm), puis :
  1. garde l'encre, le fond et les contre-formes du B ; remplit la flèche, la petite
     feuille du haut et tous les filets décoratifs ;
  2. élargit les séparations fines (feuilles / tige / B) à la largeur mini ;
  3. supprime les traits d'encre plus fins que la largeur mini, lisse les contours ;
  4. revectorise (potrace) dans logo_simple.json, lu par build_prints.py.

Usage : python3 simplify_logo.py   (dépendances : opencv-python-headless, numpy, potracer, node + playwright-core)
"""
import json
import os
import subprocess
import tempfile

import cv2
import numpy as np
import potrace

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_SVG = os.path.join(HERE, "logo-bodystart-1-couleur-vert.svg")
OUT_JSON = os.path.join(HERE, "logo_simple.json")

RASTER_W, RASTER_H = 2800, 2204
G = 63                      # largeur mini en px : 63 px = 1,8 mm à 80 mm de large
R = G // 2
PAD = 150


def disk(k):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * k + 1, 2 * k + 1))


def rasterize():
    tmp = tempfile.mkdtemp()
    html = os.path.join(tmp, "logo.html")
    png = os.path.join(tmp, "logo.png")
    with open(html, "w") as f:
        f.write(f"<html><body style='margin:0;background:#fff'>"
                f"<img src='file://{SRC_SVG}' style='width:{RASTER_W}px;display:block'></body></html>")
    subprocess.run(["node", os.path.join(HERE, "render_png.js"), html, png, str(RASTER_W), str(RASTER_H)], check=True)
    return cv2.imread(png, 0)


def simplify(im):
    im = cv2.copyMakeBorder(im, PAD, PAD, PAD, PAD, cv2.BORDER_CONSTANT, value=255)
    blk = (im < 128).astype(np.uint8)
    _, lab, _, _ = cv2.connectedComponentsWithStats(1 - blk, connectivity=4)
    background = lab[0, 0]
    counters = lab[860 + PAD, 1268 + PAD]          # contre-formes du B (zone blanche intérieure)
    ink = 1 - ((lab == background) | (lab == counters)).astype(np.uint8)

    # petite feuille du haut à gauche : contour ouvert, on remplit son intérieur
    closed = cv2.morphologyEx(ink, cv2.MORPH_CLOSE, disk(14))
    ff = closed.copy()
    cv2.floodFill(ff, np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8), (0, 0), 1)
    holes = (ff == 0).astype(np.uint8)
    nh, hl, hs, _ = cv2.connectedComponentsWithStats(holes)
    for i in range(1, nh):
        x, y, w, h, a = hs[i]
        if x + w < 800 + PAD and y > 400 + PAD and y + h < 1100 + PAD and a > 2000:
            ink[hl == i] = 1

    ni, il, ist, _ = cv2.connectedComponentsWithStats(ink)
    for i in range(1, ni):
        if ist[i, 4] < 5000:
            ink[il == i] = 0

    # élargit les séparations fines qui structurent le dessin (pas les petites encoches du contour)
    white = 1 - ink
    thin = white & (1 - cv2.morphologyEx(white, cv2.MORPH_OPEN, disk(R)))
    nt, tl, tst, _ = cv2.connectedComponentsWithStats(thin)
    keep = np.zeros_like(thin)
    for i in range(1, nt):
        if max(tst[i, 2], tst[i, 3]) > 2.5 * G:
            keep[tl == i] = 1
    ink = 1 - (white | cv2.dilate(keep, disk(R + 6)))

    ink = cv2.morphologyEx(ink, cv2.MORPH_OPEN, disk(R))
    white = 1 - ink
    nw, wl, wst, _ = cv2.connectedComponentsWithStats(white, connectivity=4)
    for i in range(1, nw):
        if wst[i, 4] < G * G * 2:
            ink[wl == i] = 1

    for _ in range(2):
        ink = (cv2.GaussianBlur(ink.astype(np.float32), (0, 0), 22) > 0.5).astype(np.uint8)
        ink = cv2.morphologyEx(ink, cv2.MORPH_OPEN, disk(R))
        ink = 1 - cv2.morphologyEx(1 - ink, cv2.MORPH_OPEN, disk(R - 4))

    ni, il, ist, _ = cv2.connectedComponentsWithStats(ink)
    for i in range(1, ni):
        if ist[i, 4] < 6 * G * G:
            ink[il == i] = 0
    return ink


def trace(ink):
    ys, xs = np.where(ink > 0)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    crop = ink[y0:y1, x0:x1].astype(bool)
    curves = potrace.Bitmap(~crop).trace(turdsize=50, alphamax=1.15, opticurve=True, opttolerance=0.3)

    def f(p):
        return f"{p.x:.1f} {p.y:.1f}"

    d = []
    for c in curves:
        d.append("M" + f(c.start_point))
        for s in c.segments:
            if s.is_corner:
                d.append("L" + f(s.c) + " L" + f(s.end_point))
            else:
                d.append("C" + f(s.c1) + " " + f(s.c2) + " " + f(s.end_point))
        d.append("Z")
    return {"w": int(x1 - x0), "h": int(y1 - y0), "d": " ".join(d)}


if __name__ == "__main__":
    data = trace(simplify(rasterize()))
    with open(OUT_JSON, "w") as fh:
        json.dump(data, fh)
    print(f"logo simplifié : {data['w']} x {data['h']} px, {len(data['d'])} caractères de tracé")

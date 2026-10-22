# T-shirt BodyStart « Varsity 78 » : commande test Black Industry

Direction C (rétro, old school gym) retenue le 22/10/2026. Premier test : t-shirt uniquement.

## Produit

| | |
|---|---|
| Modèle | RIO 250 g, coupe oversize |
| Coloris | Noir, Blanc |
| Technique | Flocage, **1 seule couleur d'encre par t-shirt** |
| Marquages | 2 par t-shirt : face (côté cœur) + dos |

## Fichiers d'impression (`impression/`)

Tous les fichiers sont **à taille réelle**, en vectoriel, **textes vectorisés** (aucune police à installer), sans fond. Chaque PDF est la copie exacte du SVG du même nom.

| Visuel | T-shirt | Encre | Taille réelle | Fichiers |
|---|---|---|---|---|
| Face, logo côté cœur | Noir | Crème #F1EADB | 80 × 63 mm | `BS-varsity78_face-coeur_80mm_encre-creme.svg` / `.pdf` |
| Face, logo côté cœur | Blanc | Vert #3B7A3F | 80 × 63 mm | `BS-varsity78_face-coeur_80mm_encre-vert.svg` / `.pdf` |
| Dos | Noir | Crème #F1EADB | 300 × 332 mm | `BS-varsity78_dos_300mm_encre-creme.svg` / `.pdf` |
| Dos | Blanc | Vert #3B7A3F | 300 × 332 mm | `BS-varsity78_dos_300mm_encre-vert.svg` / `.pdf` |

Attention : le fichier crème est clair sur fond transparent. Dans un visualiseur à fond blanc, il paraît presque vide alors qu'il est complet.

### Placement

- **Face** : logo de 8 cm de large, côté cœur (à gauche quand on porte le t-shirt). Centre du logo à environ 11 cm de l'axe du t-shirt, haut du logo à environ 10 cm sous la couture d'épaule, côté col.
- **Dos** : visuel centré, haut du visuel à 7–8 cm sous la couture du col.
- Taille unique de marquage pour toutes les tailles. Le dos fait 30 cm de large : à valider sur la plus petite taille commandée (si XS/S, demander à Black Industry s'ils préfèrent 27 cm).

### Couleurs d'encre

Les hexadécimaux sont la référence écran. En flocage, l'encre est un flex choisi dans le nuancier du fournisseur :
- crème #F1EADB → flex crème / ivoire / sable clair le plus proche ;
- vert #3B7A3F → flex vert moyen le plus proche (ni vert pomme, ni vert sapin).

**À demander à Black Industry : leur nuancier flex et un BAT** avant la production.

### Contrôle technique

Les fichiers ont été vérifiés automatiquement à 10 px/mm (dos) et 40 px/mm (face) :
- **Face : aucun trait ni jour sous 1,5 mm.** Le logo simplifié est dessiné pour 1,8 mm minimum à 8 cm de large.
- **Dos : aucun trait d'encre sous 1,5 mm**, à part la pointe de l'accent du È (0,7 mm à l'extrême pointe : c'est la forme de la lettre). Les seuls jours étroits sont des angles intérieurs de lettres (sommet du contre-poinçon du A, ergot du G, angles du N, environ 1,2 mm). Ils se découpent sans problème.
- L'accent du È de « COIGNIÈRES » a été remonté de 1,5 mm pour laisser un vrai jour entre l'accent et la lettre.

## Logo simplifié (`logo/`)

Le logo 1 couleur d'origine (`sources/logo-bodystart-1-couleur-vert.svg`) est inutilisable en flocage, même en grand. C'est un tracé automatique avec des doubles contours et des filets blancs d'environ 0,2 mm qui ne se découpent pas.

La version simplifiée garde la silhouette (le B, les feuilles, la flèche montante) et supprime les nervures, les doubles contours et les poussières. Ses traits et ses jours font au moins 1,8 mm à 8 cm de large. Elle sert à la face **et** au dos (13,8 cm de large au dos).

Elle est déclinée en noir, vert, crème et blanc pour les futurs supports (stickers, sacs, broderie à valider à part). Taille mini conseillée : 6 cm de large.

Limite : c'est une simplification du dessin existant, faite par traitement d'image. Elle est propre pour la découpe flex. Pour un usage « identité de marque » (enseigne, packaging), un redessin à la main dans Illustrator donnera des courbes plus régulières.

## Visuels Instagram (`instagram/`)

4 images 1080 × 1350 (format portrait 4:5) : noir face, noir dos, blanc face, blanc dos. Les marquages posés sur le t-shirt sont les fichiers d'impression eux-mêmes, à l'échelle réelle. Ce sont des maquettes illustrées, pas des photos : à remplacer par des photos portées une fois les t-shirts reçus.

## Mis de côté : le haut à manches longues

À trancher plus tard :
- **Sweat col rond gris chiné** : le vert #3B7A3F manque de contraste sur le gris chiné. Il faut passer à un vert foncé (#24502A) ou au noir.
- **Hoodie zippé, visuel au dos seulement** : le visuel dos actuel (300 × 332 mm) rentre tel quel dans la zone 30 × 40 cm.

## Régénérer les fichiers (`sources/`)

```bash
pip install fonttools opencv-python-headless numpy potracer
npm install playwright-core            # + un Chromium (variable CHROMIUM_PATH)
python3 sources/simplify_logo.py       # logo d'origine → sources/logo_simple.json
python3 sources/build_prints.py        # → impression/*.svg et logo/*.svg
node sources/make_pdfs.js              # → impression/*.pdf
python3 sources/build_instagram.py     # → instagram/*.png
```

Polices : Graduate et Oswald SemiBold, licence SIL Open Font License (usage commercial et merch autorisés ; textes des licences dans `sources/fonts/`).

# qr_time_sync — Mise à l'heure du lecteur Eyoyo EY-028P

Petit programme Python qui affiche **chaque seconde** un QR code contenant l'heure
locale courante, prêt à être scanné par le lecteur **Eyoyo EY-028P** pour remettre
son horloge interne à jour (celle affichée sur son écran LCD).

## Format du code

C'est le format officiel de l'appareil, retrouvé en analysant la page de
synchronisation fournie par Eyoyo dans le manuel
(`http://www.wisdomlinke.net/time.html`) :

```
^&02F&^AAAAMMJJHHMMSS
```

Exemple : `^&02F&^20261105153201` = 05/11/2026 15:32:01.

Le scanner reconnaît cette commande (QR **ou** code-barres CODE128) et met
sa propre horloge à jour ; le bip confirme l'opération. La page officielle se
rafraîchit toutes les secondes — ce programme fait pareil, en local, sans
connexion internet, et aligne l'affichage sur les frontières de secondes.

## Version web (double-clic)

`qr_time_sync.html` — page unique autonome (~23 Ko) : HTML + JavaScript embarqués,
**aucune installation ni connexion requise**. Elle s'ouvre d'un double-clic dans
n'importe quel navigateur (file://) ; `F11` passe en plein écran pour un scan
facile. Généateur embarqué : *qrcode-generator* v1.5.2 (MIT) © Kazuhiko Arase —
la même famille de bibliothèque que la page officielle Eyoyo. Rafraîchissement
aligné sur les frontières de secondes et fond blanc, comme le script terminal.

## Installation

Fait une fois (venv dédié, sans toucher à la distribution Python). Avec `uv`
(déjà installé sur cette machine) :

```bash
cd qr_time_sync
uv venv .venv
uv pip install --python .venv/bin/python qrcode pillow
```

Ou avec Python seul (si le système le permet) :

```bash
cd qr_time_sync
python3 -m venv .venv && .venv/bin/pip install qrcode pillow
```

## Utilisation

```bash
cd qr_time_sync
.venv/bin/python qr_time_sync.py
```

Puis visez l'écran avec le EY-028P : au bip, l'horloge du scanner est à jour.
`Ctrl+C` pour quitter.

### Options

| Option | Effet |
| --- | --- |
| `--scale N` | Élargit les modules (N caractères par module). Défaut 1 = modules carrés. |
| `--ecc {L,M,Q,H}` | Niveau de correction d'erreur du QR (défaut `M`). `L` donne un code plus petit. |
| `--seconds N` | S'arrête automatiquement après N affichages. |
| `--png [fichier]` | Écrit aussi le QR dans un PNG (par défaut `qr_time.png`) à chaque seconde, si vous préférez l'afficher dans une visionneuse. Nécessite Pillow. |

### Conseils de scan

- luminosité de l'écran correcte, éviter les reflets ;
- distance typique 10–20 cm, le scanner lit les codes sur écran ;
- si le bip tarde, essayez `--ecc L` (code plus petit, même contenu) ou
  augmentez plutôt la taille de police du terminal que `--scale`.
# qr_time_sync

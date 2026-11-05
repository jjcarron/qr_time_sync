#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qr_time_sync.py — Synchronisation de l'horloge du lecteur Eyoyo EY-028P.

Affiche dans le terminal un QR code contenant l'heure locale courante,
rafraîchi à chaque top de seconde (aligné sur les frontières de seconde,
comme la page officielle http://www.wisdomlinke.net/time.html dont ce
programme est une réimplémentation locale/sans internet).

Contenu encodé (reverse-engineered depuis la page officielle) :

    ^&02F&^ + AAAAMMJJHHMMSS

Exemple pour le 5 novembre 2026 à 15:32:01 :

    ^&02F&^20261105153201

C'est le même code que celui transmis par le code-barres CODE128 et le
QR code de la page officielle : il suffit de le scanner avec le EY-028P,
le bip confirme la prise en compte.

Usage :

    .venv/bin/python qr_time_sync.py
    .venv/bin/python qr_time_sync.py --scale 2 --ecc L
"""

import argparse
import datetime
import sys
import time

import qrcode

# ---------------------------------------------------------------- constantes

PREFIX = "^&02F&^"   # commande officielle de synchro date/heure du EY-028P
QUIET = 4            # quiet zone standard : 4 modules blancs autour du code

RESET = "\033[0m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
HOME = "\033[H"

ECC_LEVELS = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}

# ---------------------------------------------------------------- rendu QR


def current_payload():
    """Retourne (payload, datetime.now()) pour l'instant courant."""
    now = datetime.datetime.now()
    return PREFIX + now.strftime("%Y%m%d%H%M%S"), now


def build_matrix(payload, ecc="M"):
    """Matrice de modules : True = noir. Quiet zone de 4 modules incluse."""
    qr = qrcode.QRCode(error_correction=ECC_LEVELS[ecc], border=0)
    qr.add_data(payload)
    qr.make(fit=True)
    body = qr.get_matrix()  # listes de booléens, sans marge
    width = len(body[0]) + 2 * QUIET
    blank = [False] * width
    matrix = [blank] * QUIET
    for row in body:
        matrix.append([False] * QUIET + list(row) + [False] * QUIET)
    matrix += [blank] * QUIET
    return matrix


def render_matrix(matrix, scale=1):
    """Demi-blocs Unicode : 2 rangées de modules par ligne de terminal.

    Fond blanc (bg 107), modules noirs (fg 30) : le QR est présenté comme
    sur une feuille blanche, ce qui est idéal pour la lecture par caméra.
    """
    height = len(matrix)
    width = len(matrix[0])
    lines = []
    for y in range(0, height, 2):
        cells = []
        for x in range(width):
            top = matrix[y][x]
            bottom = matrix[y + 1][x] if y + 1 < height else False
            if top and bottom:
                style, glyph = "\033[30;40m", "█"       # noir / noir
            elif top:
                style, glyph = "\033[30;107m", "▀"      # noir / blanc
            elif bottom:
                style, glyph = "\033[30;107m", "▄"      # blanc / noir
            else:
                style, glyph = "\033[107m", " "         # blanc / blanc
            cells.append(style + glyph * scale + RESET)
        lines.append("".join(cells) + RESET + "\033[K")
    return lines


def build_frame(payload, now, scale, ecc):
    """Assemble une frame ANSI complète (QR + libellés)."""
    headers = "  Eyoyo EY-028P — synchronisation de l'horloge  (Ctrl+C pour quitter)"
    lines = [headers + "\033[K"]
    lines.extend(render_matrix(build_matrix(payload, ecc), scale))
    lines.append(f"  \033[1m{now:%Y-%m-%d %H:%M:%S}\033[0m\033[K")
    lines.append("  " + payload + "\033[K")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- mode PNG


def write_png(payload, path, ecc, warned):
    """Sauvegarde optionnelle du QR en PNG (nécessite Pillow)."""
    try:
        qr = qrcode.QRCode(error_correction=ECC_LEVELS[ecc], border=QUIET)
        qr.add_data(payload)
        qr.make(fit=True)
        qr.make_image(fill_color="black", back_color="white").save(path)
    except Exception as exc:  # pragma: no cover - dépendance optionnelle
        if not warned["png"]:
            print(f"⚠ PNG indisponible ({exc}) — installez Pillow : pip install pillow",
                  file=sys.stderr)
            warned["png"] = True


# ---------------------------------------------------------------- principal


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Affiche l'heure en QR code chaque seconde pour "
                    "mettre à l'heure un lecteur Eyoyo EY-028P.")
    parser.add_argument("--scale", type=int, default=1, metavar="N",
                        help="caractères par module en largeur (défaut : 1 = modules carrés)")
    parser.add_argument("--ecc", default="M", choices=["L", "M", "Q", "H"],
                        help="correction d'erreur du QR (défaut : M)")
    parser.add_argument("--seconds", type=int, default=0, metavar="N",
                        help="s'arrête après N secondes (0 = infini, Ctrl+C pour quitter)")
    parser.add_argument("--png", nargs="?", const="qr_time.png", default=None,
                        metavar="FICHIER",
                        help="écrit aussi le QR dans un PNG à chaque seconde (Pillow requis)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    warned = {"png": False}
    out = sys.stdout

    out.write(HIDE_CURSOR + "\033[2J\033[H")
    out.flush()

    frames = 0
    try:
        while True:
            # Plus propre : attendre le front montant de la seconde courante
            time.sleep(max(0.0, 1.0 - (time.time() % 1.0)) + 0.02)
            payload, now = current_payload()
            out.write(HOME + build_frame(payload, now, args.scale, args.ecc))
            out.flush()
            if args.png is not None:
                write_png(payload, args.png, args.ecc, warned)
            frames += 1
            if args.seconds and frames >= args.seconds:
                break
    except KeyboardInterrupt:
        pass
    finally:
        out.write(RESET + SHOW_CURSOR + "\033[2J\033[H\033[K"
                  f"Terminé après {frames} affichage(s). "
                  "Un bip du scanner confirme l'heure reçue.\033[0m\n")
        out.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrait du .ttsmod les images et PDF utiles, les met a l'echelle du plateau,
et fabrique le plan de jeu (plateau + bandeau des six zones joueurs).

    python3 tools/build_assets.py module.ttsmod [countersheet_2.pdf]
"""
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile

import io

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import components as C
from tts_assets import TTS_IMAGES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'assets', 'images')
PDF = os.path.join(ROOT, 'assets', 'pdf')

ZONE_H = 480          # hauteur du bandeau des zones joueurs
TITLE_H = 46


def index_archive(path):
    idx = {}
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            m = re.search(r'ugc(\d+)([0-9A-Fa-f]{40})', os.path.basename(n))
            if m:
                idx[(m.group(1), m.group(2).upper())] = n
    return idx


def load(z, index, key, tmp):
    ugc, digest = key[0], key[1].upper()
    member = index[(ugc, digest)]
    dest = os.path.join(tmp, os.path.basename(member))
    with z.open(member) as src, open(dest, 'wb') as out:
        shutil.copyfileobj(src, out)
    return dest


def save_counter(src, name, box):
    with Image.open(src) as im:
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        im.thumbnail(box, Image.LANCZOS)
        dest = os.path.join(IMG, name + '.png')
        im.convert('RGB').save(dest, optimize=True)
        return im.size


def find_font(size):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def build_playmat(board_path):
    """Plateau + bandeau parchemin contenant les six zones joueurs."""
    board = Image.open(board_path).convert('RGB')
    W, H = board.size
    mat = Image.new('RGB', (W, H + ZONE_H), (238, 230, 210))

    # fond : on echantillonne une zone de parchemin vierge du plateau
    patch = board.crop((2750, 2330, 2950, 2470))
    for x in range(0, W, patch.width):
        for y in range(H, H + ZONE_H, patch.height):
            mat.paste(patch, (x, y))
    mat.paste(board, (0, 0))

    d = ImageDraw.Draw(mat)
    font = find_font(34)
    col_w = W // len(C.CURRENTS)
    for i, cur in enumerate(C.CURRENTS):
        x0 = i * col_w + 8
        x1 = (i + 1) * col_w - 8
        y0 = H + 10
        y1 = H + ZONE_H - 10
        d.rounded_rectangle([x0, y0, x1, y1], radius=18,
                            outline=(120, 100, 70), width=3)
        d.text(((x0 + x1) // 2, y0 + TITLE_H // 2), cur, fill=(60, 45, 25),
               font=font, anchor='mm')
    return mat


def zone_layout(width, height, n_slots):
    """Positions (en pixels, relatives a la zone) des emplacements de pions."""
    cols, rows = 3, 2
    cell = C.COUNTER_PX + 12
    ox = 26
    oy = TITLE_H + 18
    return [(ox + (k % cols) * cell + C.COUNTER_PX // 2,
             oy + (k // cols) * cell + C.COUNTER_PX // 2) for k in range(n_slots)]


def board_to_pixels(x, z):
    """Convertit une position du plateau TTS en pixels du plan de jeu."""
    w, h = C.BOARD_PX
    world_h = C.WORLD_W * h / w
    cx, cz = C.BOARD_CENTER
    u = 0.5 + (x - cx) / C.WORLD_W
    v = 0.5 - (z - cz) / world_h
    return int(round(u * w)), int(round(v * h))


def extract_setup(ttsmod, index):
    """Releve la mise en place initiale du mod TTS et la convertit en pixels.

    Seuls les pions qui tombent sur le plateau sont retenus : les personnalites
    et l'argent sont replaces par nos soins dans les zones joueurs.
    """
    with zipfile.ZipFile(ttsmod) as z:
        name = [n for n in z.namelist() if n.endswith('.json')][0]
        data = json.loads(z.read(name).decode('utf-8'))

    by_hash = {}
    for idx, (ugc, digest, _ext, _n) in TTS_IMAGES.items():
        by_hash[digest.upper()] = idx
    idx_to_base = {idx: base for base, _l, _c, _cur, idx in C.PIECES}

    w, h = C.BOARD_PX
    on_board = []
    for o in data['ObjectStates']:
        ci = o.get('CustomImage') or {}
        m = re.search(r'/ugc/\d+/([0-9A-Fa-f]{40})', ci.get('ImageURL') or '')
        if not m:
            continue
        idx = by_hash.get(m.group(1).upper())
        base = idx_to_base.get(idx)
        if base is None:            # personnalites et decors : traites a part
            continue
        t = o['Transform']
        px, py = board_to_pixels(t['posX'], t['posZ'])
        if 0 <= px < w and 0 <= py < h:
            on_board.append({'piece': base, 'x': px, 'y': py})
    on_board.sort(key=lambda e: (e['piece'], e['y'], e['x']))
    return on_board


def player_zone_setup(board_h, board_w):
    """Place les personnalites et les assignats de depart dans les zones joueurs."""
    col_w = board_w // len(C.CURRENTS)
    # Montants de depart (regles §4.6), en billets de 50 livres
    money = {'Sans-Culotte': 7, 'Montagne': 7, 'Gironde': 28,
             'Marais': 16, 'Feuillant': 28, 'Royaliste': 8}
    entries = []
    for i, cur in enumerate(C.CURRENTS):
        persons = [p for p in C.PERSONALITIES if p[2] == cur]
        spots = zone_layout(col_w, ZONE_H, len(persons))
        for (base, _lbl, _cur, _idx, _alts), (dx, dy) in zip(persons, spots):
            entries.append({'piece': base, 'kind': 'personnalite',
                            'x': i * col_w + dx, 'y': board_h + dy})
        entries.append({'piece': 'assignat_50', 'kind': 'assignats',
                        'count': money[cur],
                        'x': i * col_w + col_w - 150,
                        'y': board_h + TITLE_H + 110})
    # Tresorerie du Gouvernement : 2300 livres (§4.6)
    entries.append({'piece': 'assignat_50', 'kind': 'assignats', 'count': 46,
                    'x': board_w // 2, 'y': board_h + ZONE_H - 120})
    return entries


def render_charts():
    """Convertit les tableaux courts en images pour la fenetre « Aides de jeu »."""
    import pymupdf
    out = []
    for src, _tab, pages in C.CHARTS:
        doc = pymupdf.open(os.path.join(PDF, src + '.pdf'))
        for pno, _title in pages:
            pix = doc[pno - 1].get_pixmap(dpi=C.CHART_DPI)
            im = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
            name = 'aide_%s_%d.png' % (src, pno)
            im.convert('P', palette=Image.ADAPTIVE, colors=64).save(
                os.path.join(IMG, name), optimize=True)
            out.append((name, im.size))
    return out


def extract_deputy_counters(countersheet):
    """Decoupe les deputes de valeur dans la planche vectorielle."""
    import pymupdf
    doc = pymupdf.open(countersheet)
    X = [50, 94, 138, 182, 227, 271, 315, 359, 439, 483, 527, 571, 615, 660, 704, 748]
    Y = [37, 81, 134, 178, 231, 275, 328, 372, 425, 469]
    SIZE, DPI = 44.1, 300
    k = DPI / 72.0
    pages = {}
    out = []
    for (current, value), ref in C.DEPUTY_SHEET.items():
        m = re.match(r'p(\d)_c(\d+)_r(\d+)$', ref)
        pno, col, row = int(m.group(1)) - 1, int(m.group(2)), int(m.group(3))
        if pno not in pages:
            pix = doc[pno].get_pixmap(dpi=DPI)
            pages[pno] = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
        box = (int(X[col] * k), int(Y[row] * k),
               int((X[col] + SIZE) * k), int((Y[row] + SIZE) * k))
        im = pages[pno].crop(box)
        im.thumbnail((C.COUNTER_PX, C.COUNTER_PX), Image.LANCZOS)
        name = 'depute_%s_%d' % (C.CURRENT_SLUG[current], value)
        im.save(os.path.join(IMG, name + '.png'), optimize=True)
        out.append((name, im.size))
    return out


def main(ttsmod, countersheet=None):
    os.makedirs(IMG, exist_ok=True)
    os.makedirs(PDF, exist_ok=True)
    index = index_archive(ttsmod)
    tmp = tempfile.mkdtemp()
    written = []

    with zipfile.ZipFile(ttsmod) as z:
        # --- plateau et plan de jeu ---
        board_src = load(z, index, C.BOARD_UGC, tmp)
        mat = build_playmat(board_src)
        mat.save(os.path.join(IMG, 'plan_de_jeu.jpg'), quality=88, optimize=True)
        written.append(('plan_de_jeu.jpg', mat.size))

        # --- pions ordinaires ---
        for base, _lbl, _cat, _cur, idx in C.PIECES:
            ugc, digest, ext, _n = TTS_IMAGES[idx]
            src = load(z, index, (ugc, digest), tmp)
            box = ((C.ASSIGNAT_PX, C.ASSIGNAT_PX) if base == 'assignat_50'
                   else (C.COUNTER_PX, C.COUNTER_PX))
            written.append((base, save_counter(src, base, box)))

        # --- personnalites : face de depart + faces alternatives ---
        for base, _lbl, cur, idx, alts in C.PERSONALITIES:
            ugc, digest, ext, _n = TTS_IMAGES[idx]
            src = load(z, index, (ugc, digest), tmp)
            name = '%s__%s' % (base, C.CURRENT_SLUG[cur])
            written.append((name, save_counter(src, name, (C.COUNTER_PX, C.COUNTER_PX))))
            for other in alts:
                src = load(z, index, C.ALT[(base, other)], tmp)
                name = '%s__%s' % (base, C.CURRENT_SLUG[other])
                written.append((name, save_counter(src, name, (C.COUNTER_PX, C.COUNTER_PX))))

        # --- deputes de valeur 1 (visuel du mod TTS) ---
        for cur, idx in C.DEPUTY_TTS.items():
            ugc, digest, ext, _n = TTS_IMAGES[idx]
            src = load(z, index, (ugc, digest), tmp)
            name = 'depute_%s_1' % C.CURRENT_SLUG[cur]
            written.append((name, save_counter(src, name, (C.COUNTER_PX, C.COUNTER_PX))))

        # --- symboles de courant ---
        for cur, idx in C.SYMBOLS.items():
            ugc, digest, ext, _n = TTS_IMAGES[idx]
            src = load(z, index, (ugc, digest), tmp)
            name = 'symbole_' + C.CURRENT_SLUG[cur]
            written.append((name, save_counter(src, name, (C.COUNTER_PX, C.COUNTER_PX))))

        # --- aides de jeu ---
        pdfs = {}
        for (ugc, digest), member in index.items():
            if member.lower().endswith('.pdf'):
                pdfs[digest[-6:].upper()] = member
        for tail, name, _title in C.PDFS:
            member = pdfs[tail.upper()]
            with z.open(member) as src, open(os.path.join(PDF, name + '.pdf'), 'wb') as out:
                shutil.copyfileobj(src, out)
            written.append((name + '.pdf', None))

        if countersheet:
            written.extend(extract_deputy_counters(countersheet))
        written.extend(render_charts())

        setup = {'board': extract_setup(ttsmod, index),
                 'zones': player_zone_setup(C.BOARD_PX[1], C.BOARD_PX[0])}
        with open(os.path.join(ROOT, 'assets', 'setup.json'), 'w') as fh:
            json.dump(setup, fh, indent=1)
        written.append(('setup.json  (%d pions plateau, %d en zone)'
                        % (len(setup['board']), len(setup['zones'])), None))

    shutil.rmtree(tmp, ignore_errors=True)
    for name, size in written:
        print('%-36s %s' % (name, ('%dx%d' % size) if size else ''))
    print('\n%d fichiers ecrits' % len(written))


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    main(*sys.argv[1:])

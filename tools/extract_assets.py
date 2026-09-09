#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrait du module Tabletop Simulator (.ttsmod) les images et PDF utiles,
les renomme lisiblement et les met a l'echelle du plateau, dans assets/.

    python3 tools/extract_assets.py chemin/vers/module.ttsmod
"""
import os
import re
import shutil
import sys
import tempfile
import zipfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from components import (ASSIGNAT_WIDTH, BOARD_UGC, COMPONENTS, COUNTER_SIZE,
                        PDFS, VERSOS)
from tts_assets import TTS_IMAGES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_OUT = os.path.join(ROOT, 'assets', 'images')
PDF_OUT = os.path.join(ROOT, 'assets', 'pdf')


def index_archive(path):
    """Renvoie {(ugc_id, hash): membre_du_zip} pour toutes les entrees du .ttsmod."""
    index = {}
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            m = re.search(r'ugc(\d+)([0-9A-Fa-f]{40})', os.path.basename(name))
            if m:
                index[(m.group(1), m.group(2).upper())] = name
    return index


def extract(z, member, dest):
    with z.open(member) as src, open(dest, 'wb') as out:
        shutil.copyfileobj(src, out)


def resize(src, dest, box):
    """Redimensionne en conservant le ratio, sans jamais agrandir."""
    with Image.open(src) as im:
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        im.thumbnail(box, Image.LANCZOS)
        if dest.lower().endswith('.png'):
            im.save(dest, optimize=True)
        else:
            im.convert('RGB').save(dest, quality=92, optimize=True)
        return im.size


def main(ttsmod):
    os.makedirs(IMG_OUT, exist_ok=True)
    os.makedirs(PDF_OUT, exist_ok=True)
    index = index_archive(ttsmod)
    tmp = tempfile.mkdtemp()
    written = []

    with zipfile.ZipFile(ttsmod) as z:
        # --- plateau ---
        raw = os.path.join(tmp, 'board_raw.jpg')
        extract(z, index[BOARD_UGC], raw)
        shutil.copyfile(raw, os.path.join(IMG_OUT, 'plateau.jpg'))
        with Image.open(raw) as im:
            written.append(('plateau.jpg', im.size))

        # --- pions ---
        wanted = {idx: name for idx, name, _, _, _, _ in COMPONENTS}
        wanted.update(VERSOS)
        for idx, name in sorted(wanted.items()):
            ugc, digest, ext, _ = TTS_IMAGES[idx]
            member = index[(ugc, digest)]
            raw = os.path.join(tmp, 'p%d.%s' % (idx, ext))
            extract(z, member, raw)
            out_ext = 'png' if ext.lower() == 'png' else 'jpg'
            dest = os.path.join(IMG_OUT, '%s.%s' % (name, out_ext))
            box = ((ASSIGNAT_WIDTH, ASSIGNAT_WIDTH) if name == 'assignat_50'
                   else (COUNTER_SIZE, COUNTER_SIZE))
            written.append((os.path.basename(dest), resize(raw, dest, box)))

        # --- aides de jeu ---
        by_tail = {}
        for (ugc, digest), member in index.items():
            if member.lower().endswith('.pdf'):
                by_tail[digest[-6:].upper()] = member
        for tail, name, _title in PDFS:
            member = by_tail[tail.upper()]
            extract(z, member, os.path.join(PDF_OUT, name + '.pdf'))
            written.append((name + '.pdf', None))

    shutil.rmtree(tmp, ignore_errors=True)
    for name, size in written:
        print('%-34s %s' % (name, '%dx%d' % size if size else ''))
    print('\n%d fichiers ecrits dans assets/' % len(written))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])

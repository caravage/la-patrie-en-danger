#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genere le module VASSAL (.vmod) a partir de assets/.

    python3 tools/build_module.py

Produit dist/La_Revolution_francaise_La_patrie_en_danger.vmod
"""
import json
import os
import sys
import zipfile
from xml.sax.saxutils import escape, quoteattr

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import components as C
import vassal_encode as V

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'assets', 'images')
PDF = os.path.join(ROOT, 'assets', 'pdf')
DIST = os.path.join(ROOT, 'dist')

MODULE_NAME = 'La Revolution francaise : La patrie en danger 1791-1795'
MODULE_VERSION = '1.0'
MODULE_DESC = ("Conversion du mod Tabletop Simulator. Jeu (c) 1995 Azure Wish "
               "Enterprise, illustrations (c) 2021 Ilya Kudriashov.")
VASSAL_VERSION = '3.7.27'
BOARD_NAME = 'Plan de jeu'
MAP_NAME = 'Plan de jeu'

FLIP_KEY = V.keystroke(70)     # Ctrl+F : changer de courant


class Builder:
    def __init__(self):
        self.gpid = 0
        self.sizes = {}

    def next_gpid(self):
        self.gpid += 1
        return self.gpid

    def size_of(self, image):
        if image not in self.sizes:
            with Image.open(os.path.join(IMG, image)) as im:
                self.sizes[image] = im.size
        return self.sizes[image]

    # --- definitions de pieces -------------------------------------------
    def personality(self, base, label, current, alts):
        """Personnalite. Si elle peut changer de camp, une couche porte une
        image par courant possible et un clic droit les fait defiler."""
        gpid = self.next_gpid()
        currents = [current] + list(alts)
        images = ['%s__%s.png' % (base, C.CURRENT_SLUG[c]) for c in currents]
        if len(currents) == 1:
            traits = [V.delete(),
                      V.marker(['Categorie', 'Courant'], ['Personnalite', current]),
                      V.basic_piece(images[0], label, gpid)]
            return gpid, V.build_piece(traits), self.size_of(images[0])
        traits = [
            V.delete(),
            V.layer(images, ['+ (%s)' % c for c in currents],
                    'Changer de courant', FLIP_KEY,
                    layer_name='Courant', description='Courant actuel'),
            V.marker(['Categorie', 'Courant'], ['Personnalite', current]),
            V.basic_piece('', label, gpid),
        ]
        return gpid, V.build_piece(traits), self.size_of(images[0])

    def deputy(self, current, value):
        """Depute de valeur. Un clic droit le fait passer d'un courant a
        l'autre (§7.5.2.1), parmi ceux qui disposent de cette valeur."""
        gpid = self.next_gpid()
        order = [c for c in C.CURRENTS if value in C.deputy_values(c)]
        images = ['depute_%s_%d.png' % (C.CURRENT_SLUG[c], value) for c in order]
        label = 'Depute %s (%d)' % (current, value)
        traits = [
            V.delete(),
            V.layer(images, ['Depute %s (%d)' % (c, value) for c in order],
                    'Changer de courant', FLIP_KEY, layer_name='Courant',
                    description='Courant du depute',
                    start_level=order.index(current) + 1),
            V.marker(['Categorie', 'Valeur'], ['Depute', str(value)]),
            V.basic_piece('', label, gpid),
        ]
        return gpid, V.build_piece(traits), self.size_of(images[0]), label

    def treasury(self, current, amount):
        """Compteur numerique d'assignats : +/- et saisie directe."""
        gpid = self.next_gpid()
        label = 'Tresorerie %s' % current
        commands = [
            ('+ 50', V.keystroke(49), ('I', 50)),
            ('+ 100', V.keystroke(50), ('I', 100)),
            ('+ 200', V.keystroke(51), ('I', 200)),
            ('- 50', V.keystroke(52), ('I', -50)),
            ('- 100', V.keystroke(53), ('I', -100)),
            ('- 200', V.keystroke(54), ('I', -200)),
            ('Fixer le montant', V.keystroke(77), ('R', 'Montant en livres')),
        ]
        traits = [
            V.labeler('$Montant$', font_size=30, bg='255,255,255',
                      description='Montant en livres'),
            V.dynamic_property('Montant', commands, value=str(amount),
                               description='Assignats detenus'),
            V.marker(['Categorie', 'Courant'], ['Tresorerie', current]),
            V.basic_piece('assignat_50.png', label, gpid),
        ]
        return gpid, V.build_piece(traits), self.size_of('assignat_50.png'), label

    def simple(self, base, label, category, current):
        gpid = self.next_gpid()
        image = base + '.png'
        keys, vals = ['Categorie'], [category]
        if current:
            keys.append('Courant'); vals.append(current)
        traits = [V.delete(), V.marker(keys, vals),
                  V.basic_piece(image, label, gpid)]
        return gpid, V.build_piece(traits), self.size_of(image)


def slot(entry_name, gpid, definition, size):
    return ('<VASSAL.build.widget.PieceSlot entryName=%s gpid="%d" height="%d" width="%d">%s'
            '</VASSAL.build.widget.PieceSlot>'
            % (quoteattr(entry_name), gpid, size[1], size[0], escape(definition)))


def setup_stack(name, x, y, inner):
    return ('<VASSAL.build.module.map.SetupStack name=%s owningBoard=%s '
            'useGridLocation="false" x="%d" y="%d">%s'
            '</VASSAL.build.module.map.SetupStack>'
            % (quoteattr(name), quoteattr(BOARD_NAME), x, y, inner))


def build():
    b = Builder()
    defs = {}          # base -> (gpid, definition, size, libelle, categorie)

    for base, label, current, _idx, alts in C.PERSONALITIES:
        gpid, d, size = b.personality(base, label, current, alts)
        defs[base] = (gpid, d, size, label, 'personnalite')

    for base, label, cat, current, _idx in C.PIECES:
        gpid, d, size = b.simple(base, label, cat, current)
        defs[base] = (gpid, d, size, label, cat)

    for cur in C.CURRENTS:
        for val in C.deputy_values(cur):
            gpid, d, size, label = b.deputy(cur, val)
            defs['depute_%s_%d' % (C.CURRENT_SLUG[cur], val)] = (gpid, d, size, label, 'depute')

    for cur in C.CURRENTS:
        gpid, d, size, label = b.treasury(cur, C.TREASURY[cur])
        defs['tresorerie_' + C.CURRENT_SLUG[cur]] = (gpid, d, size, label, 'tresorerie')
    gpid, d, size, label = b.treasury('Gouvernement', C.TREASURY_GOVERNMENT)
    defs['tresorerie_gouvernement'] = (gpid, d, size, label, 'tresorerie')

    # ---- palette --------------------------------------------------------
    def panel(title, bases, cols=6):
        slots = []
        for base in bases:
            gpid, d, size, label, _cat = defs[base]
            # chaque entree de palette a besoin de son propre gpid
            g = b.next_gpid()
            d2 = d.replace(';%d;0' % gpid, ';%d;0' % g)
            slots.append(slot(label, g, d2, size))
        return ('<VASSAL.build.widget.PanelWidget entryName=%s fixed="false" '
                'nColumns="%d" vert="false">%s</VASSAL.build.widget.PanelWidget>'
                % (quoteattr(title), cols, ''.join(slots)))

    panels = []
    for cur in C.CURRENTS:
        bases = [p[0] for p in C.PERSONALITIES if p[2] == cur]
        panels.append(panel('Personnalites - ' + cur, bases, cols=3))
    panels.append(panel('Deputes', ['depute_%s_%d' % (C.CURRENT_SLUG[c], v)
                                    for c in C.CURRENTS for v in C.deputy_values(c)], 5))
    panels.append(panel('Controle et revolte', [p[0] for p in C.PIECES if p[2] == 'controle'], 4))
    panels.append(panel('Armees', [p[0] for p in C.PIECES if p[2] == 'armee'], 6))
    panels.append(panel('Marqueurs de piste', [p[0] for p in C.PIECES if p[2] == 'piste'], 5))
    panels.append(panel('Assignats', ['assignat_50']
                        + ['tresorerie_' + C.CURRENT_SLUG[c] for c in C.CURRENTS]
                        + ['tresorerie_gouvernement'], 4))
    palette = ('<VASSAL.build.module.PieceWindow name="Pions" text="Pions" '
               'tooltip="Ouvrir la boite de pions" hidden="false" scale="1.0" '
               'defaultWidth="0" hotkey="">'
               '<VASSAL.build.widget.TabWidget entryName="Pions">%s</VASSAL.build.widget.TabWidget>'
               '</VASSAL.build.module.PieceWindow>' % ''.join(panels))

    # ---- mise en place --------------------------------------------------
    setup = json.load(open(os.path.join(ROOT, 'assets', 'setup.json')))
    stacks = []
    for e in setup['board']:
        # les deputes du mod TTS sont ignores : l'Assemblee est recomposee
        # plus bas d'apres les regles §4.5, avec des pions de valeur
        if e['piece'].startswith('depute'):
            continue
        gpid, d, size, label, _cat = defs[e['piece']]
        g = b.next_gpid()
        d2 = d.replace(';%d;0' % gpid, ';%d;0' % g)
        stacks.append(setup_stack(label, e['x'], e['y'], slot(label, g, d2, size)))

    def place(base, x, y, name=None):
        gpid, d, size, label, _cat = defs[base]
        g = b.next_gpid()
        d2 = d.replace(';%d;0' % gpid, ';%d;0' % g)
        stacks.append(setup_stack(name or label, x, y, slot(label, g, d2, size)))

    # personnalites dans la zone de leur camp
    for e in setup['zones']:
        if e.get('kind') == 'personnalite':
            place(e['piece'], e['x'], e['y'])

    # tresoreries : une par camp, plus celle du Gouvernement
    zone_x = {e['piece']: e for e in setup['zones'] if e.get('kind') == 'assignats'}
    board_w, board_h = C.BOARD_PX
    col_w = board_w // len(C.CURRENTS)
    for i, cur in enumerate(C.CURRENTS):
        place('tresorerie_' + C.CURRENT_SLUG[cur],
              i * col_w + col_w - 150, board_h + 200)
    place('tresorerie_gouvernement', board_w // 2, board_h + 430)

    # Assemblee nationale : composition des regles §4.5, en pions de valeur
    for cur, total in C.ASSEMBLY.items():
        ax, ay = C.ASSEMBLY_ANCHORS[cur]
        remaining = total
        inner = []
        for val in sorted(C.deputy_values(cur), reverse=True):
            while remaining >= val:
                gpid, d, size, label, _cat = defs['depute_%s_%d' % (C.CURRENT_SLUG[cur], val)]
                g = b.next_gpid()
                inner.append(slot(label, g, d.replace(';%d;0' % gpid, ';%d;0' % g), size))
                remaining -= val
        stacks.append(setup_stack('Deputes %s (%d)' % (cur, total),
                                  ax, ay, ''.join(inner)))

    # ---- carte ----------------------------------------------------------
    map_parts = [
        '<VASSAL.build.module.map.BoardPicker addColumnText="" addRowText="" '
        'boardPrompt="Choisir le plan de jeu" slotHeight="125" slotScale="0.2" slotWidth="350">'
        '<VASSAL.build.module.map.boardPicker.Board image="plan_de_jeu.jpg" name=%s '
        'reversible="false" color="255,255,255" width="0" height="0"/>'
        '</VASSAL.build.module.map.BoardPicker>' % quoteattr(BOARD_NAME),
        '<VASSAL.build.module.map.StackMetrics bottom="8" disabled="false" exSepX="14" '
        'exSepY="20" left="8" right="8" top="8" unexSepX="8" unexSepY="18"/>',
        '<VASSAL.build.module.map.ImageSaver/>',
        '<VASSAL.build.module.map.TextSaver/>',
        '<VASSAL.build.module.map.ForwardToKeyBuffer/>',
        '<VASSAL.build.module.map.Scroller/>',
        '<VASSAL.build.module.map.ForwardToChatter/>',
        '<VASSAL.build.module.map.MenuDisplayer/>',
        '<VASSAL.build.module.map.KeyBufferer/>',
        '<VASSAL.build.module.map.PieceMover/>',
        '<VASSAL.build.module.map.HighlightLastMoved/>',
        '<VASSAL.build.module.map.StackExpander/>',
        '<VASSAL.build.module.map.PieceRecenterer/>',
        '<VASSAL.build.module.map.Zoomer zoomLevels="0.4,0.55,0.75,1.0" zoomStart="2"/>',
        '<VASSAL.build.module.map.CounterDetailViewer borderThickness="2" centerAll="false" '
        'delay="500" description="Loupe" display="true" fgColor="0,0,0" bgColor="255,255,204" '
        'minDisplayPieces="1" showgraph="true" showgraphsingle="true" showtext="false" '
        'zoomlevel="1.5" version="3"/>',
    ]
    the_map = ('<VASSAL.build.module.Map mapName=%s markMoved="Never" '
               'allowMultiple="false" backgroundcolor="238,230,210" '
               'changeFormat="$message$" color="255,0,0" createFormat="$pieceName$ place en $location$" '
               'edgeHeight="0" edgeWidth="0" hideKey="" highlightThickness="3" '
               'launch="false" moveKey="" moveToFormat="$pieceName$ : $previousLocation$ -&gt; $location$" '
               'moveWithinFormat="$pieceName$ : $previousLocation$ -&gt; $location$" '
               'onlyReportChangedLocation="false" showKey="" thickness="3" '
               'buttonName="" icon="" tooltip="">%s%s</VASSAL.build.module.Map>'
               % (quoteattr(MAP_NAME), ''.join(map_parts), ''.join(stacks)))

    # ---- fenetre « Aides de jeu » : tableaux consultables dans VASSAL ----
    def chart(title, image):
        return ('<VASSAL.build.widget.Chart chartName=%s description="" fileName=%s/>'
                % (quoteattr(title), quoteattr(image)))

    tabs = []
    for src, tab_title, pages in C.CHARTS:
        if len(pages) == 1:
            tabs.append(chart(tab_title, 'aide_%s_%d.png' % (src, pages[0][0])))
        else:
            inner = ''.join(chart(t, 'aide_%s_%d.png' % (src, pno)) for pno, t in pages)
            tabs.append('<VASSAL.build.widget.TabWidget entryName=%s>%s'
                        '</VASSAL.build.widget.TabWidget>' % (quoteattr(tab_title), inner))
    charts = ('<VASSAL.build.module.ChartWindow name="Aides de jeu" '
              'text="Aides" tooltip="Tableaux de jeu" icon="" hotkey="" description="">'
              '<VASSAL.build.widget.TabWidget entryName="Aides de jeu">%s'
              '</VASSAL.build.widget.TabWidget></VASSAL.build.module.ChartWindow>'
              % ''.join(tabs))

    # ---- aides de jeu ---------------------------------------------------
    docs = ''.join(
        '<VASSAL.build.module.documentation.BrowserPDFFile pdfFile=%s title=%s/>'
        % (quoteattr('pdf/%s.pdf' % name), quoteattr(title))
        for _tail, name, title in C.PDFS)

    roster = ('<VASSAL.build.module.PlayerRoster buttonText="Camp" '
              'buttonTooltip="Choisir ou changer de camp" icon="" buttonKeyStroke="">%s'
              '</VASSAL.build.module.PlayerRoster>'
              % ''.join('<entry>%s</entry>' % escape(c) for c in C.CURRENTS))

    dice = ''.join(
        '<VASSAL.build.module.DiceButton addToTotal="0" hotkey="" icon="" '
        'lockAdd="false" lockDice="false" lockPlus="false" lockSides="false" '
        'nDice="%d" nSides="6" name=%s plus="0" prompt="false" '
        'reportFormat="** $name$ = $result$ ***" reportTotal="%s" '
        'sortDice="false" text=%s tooltip=%s keepDice="false" keepOption="&gt;" keepCount="1"/>'
        % (n, quoteattr(label), 'true' if n > 1 else 'false',
           quoteattr(label), quoteattr('Lancer ' + label))
        for n, label in ((1, '1d6'), (2, '2d6')))

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<VASSAL.build.GameModule name=%s version=%s description=%s '
        'VassalVersion=%s nextPieceSlotId="%d" ModuleOther1="" ModuleOther2="">'
        # l'encodeur doit venir en premier : sans lui, aucune piece ne se decode
        '<VASSAL.build.module.BasicCommandEncoder/>'
        '<VASSAL.build.module.Documentation>%s</VASSAL.build.module.Documentation>'
        '<VASSAL.build.module.GlobalOptions autoReport="Use Preferences Setting" '
        'centerOnMove="Use Preferences Setting" nonOwnerUnmaskable="Never" '
        'promptString="Choisir un camp" playerIdFormat="$playerName$" '
        'chatterHTMLSupport="Always"/>'
        '%s'
        '<VASSAL.build.module.NotesWindow buttonText="Notes" '
        'tooltip="Notes de partie et promesses secretes" icon="/images/notes.gif" hotkey=""/>'
        '%s%s%s%s'
        '<VASSAL.build.module.Inventory name="Inventaire" buttonText="Inventaire" '
        'tooltip="Lister les pions en jeu" icon="" hotkey="" '
        'groupBy="Categorie" sortStrategy="Alphabetically" include="{true}" '
        'zoom="1.0" drawPieces="true" foldersOnly="false" showMenu="true" '
        'sides="" centerOnPiece="true" forwardKeystroke="true" '
        'leafFormat="$PieceName$" nonLeafFormat="$PropertyValue$" '
        'label="Pions en jeu" launchFunction="functionHide" refreshHotkey="" '
        'sortFormat="$PieceName$" pieceZoom="0.33" pieceZoom2="0.6" pieceZoom3="1.0"/>'
        '</VASSAL.build.GameModule>'
        % (quoteattr(MODULE_NAME), quoteattr(MODULE_VERSION), quoteattr(MODULE_DESC),
           quoteattr(VASSAL_VERSION), b.gpid + 100, docs, roster, charts,
           the_map, palette, dice)
    )
    return xml, b


def main():
    os.makedirs(DIST, exist_ok=True)
    xml, b = build()
    moduledata = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<data version="1">'
        '<version>%s</version><VassalVersion>%s</VassalVersion>'
        '<name>%s</name><description>%s</description><dateSaved>0</dateSaved></data>'
        % (MODULE_VERSION, VASSAL_VERSION, escape(MODULE_NAME), escape(MODULE_DESC)))

    out = os.path.join(DIST, 'La_Revolution_francaise_La_patrie_en_danger.vmod')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('buildFile.xml', xml.encode('utf-8'))
        z.writestr('moduledata', moduledata.encode('utf-8'))
        for f in sorted(os.listdir(IMG)):
            z.write(os.path.join(IMG, f), 'images/' + f)
        for f in sorted(os.listdir(PDF)):
            z.write(os.path.join(PDF, f), 'pdf/' + f)
    print('%s  (%.1f Mo, %d emplacements de pions)'
          % (out, os.path.getsize(out) / 1e6, b.gpid))


if __name__ == '__main__':
    main()

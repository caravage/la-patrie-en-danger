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
MODULE_DESC = ("Conversion of the Tabletop Simulator mod. Game (c) 1995 Azure "
               "Wish Enterprise, artwork (c) 2021 Ilya Kudriashov.")
VASSAL_VERSION = '3.7.27'
BOARD_NAME = 'Game Board'
MAP_NAME = 'Game Board'

FLIP_KEY = V.keystroke(70)      # Ctrl+F : change current affiliation
ARREST_KEY = V.keystroke(65)    # Ctrl+A : Arrest
GUILLOTINE_KEY = V.keystroke(71)  # Ctrl+G : Guillotine
HIDE_KEY = V.keystroke(72)      # Ctrl+H : Hide/Reveal a secret note

# Commandes de compteur (+/- avec report), reutilisees pour les 4 pistes et
# les 7 marqueurs de Fame.
TRACK_COMMANDS = [
    ('+1', V.keystroke(49), ('I', 1)),
    ('-1', V.keystroke(50), ('I', -1)),
    ('+5', V.keystroke(51), ('I', 5)),
    ('-5', V.keystroke(52), ('I', -5)),
    ('Set Value', V.keystroke(77), ('R', 'New value (1-20)')),
]
TRACK_KEYS = [k for _l, k, _c in TRACK_COMMANDS]

TREASURY_COMMANDS = [
    ('+ 50', V.keystroke(49), ('I', 50)),
    ('+ 100', V.keystroke(50), ('I', 100)),
    ('+ 200', V.keystroke(51), ('I', 200)),
    ('- 50', V.keystroke(52), ('I', -50)),
    ('- 100', V.keystroke(53), ('I', -100)),
    ('- 200', V.keystroke(54), ('I', -200)),
    ('Set Amount', V.keystroke(77), ('R', 'Amount (livres)')),
]
TREASURY_KEYS = [k for _l, k, _c in TREASURY_COMMANDS]


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
        """Personnalite : non supprimable. Menu contextuel "Arrest" (deplace
        vers la Prison du Temple, §3.2.3.2) et "Guillotine" (§3.2.3.3). Si
        elle peut changer de camp, une couche porte une image par courant
        possible et un clic droit la fait defiler (§7.3.2)."""
        gpid = self.next_gpid()
        currents = [current] + list(alts)
        images = ['%s__%s.png' % (base, C.CURRENT_SLUG[c]) for c in currents]
        arrest = V.send_to_location('Arrest', ARREST_KEY, C.PRISON_XY[0], C.PRISON_XY[1],
                                    MAP_NAME, BOARD_NAME, description='Send to Prison du Temple')
        guillotine = V.send_to_location('Guillotine', GUILLOTINE_KEY,
                                        C.GUILLOTINE_XY[0], C.GUILLOTINE_XY[1],
                                        MAP_NAME, BOARD_NAME, description='Send to Madame Guillotine')
        if len(currents) == 1:
            traits = [arrest, guillotine,
                      V.marker(['Category', 'Current'], ['Personality', current]),
                      V.basic_piece(images[0], label, gpid)]
            return gpid, V.build_piece(traits), self.size_of(images[0])
        traits = [
            arrest, guillotine,
            V.layer(images, ['+ (%s)' % c for c in currents],
                    'Change Current', FLIP_KEY,
                    layer_name='Current', description='Current affiliation'),
            V.marker(['Category', 'Current'], ['Personality', current]),
            V.basic_piece('', label, gpid),
        ]
        return gpid, V.build_piece(traits), self.size_of(images[0])

    def deputy(self, current, value):
        """Depute de valeur. Un clic droit le fait passer d'un courant a
        l'autre (§7.5.2.1), parmi ceux qui disposent de cette valeur."""
        gpid = self.next_gpid()
        order = [c for c in C.CURRENTS if value in C.deputy_values(c)]
        images = ['depute_%s_%d.png' % (C.CURRENT_SLUG[c], value) for c in order]
        label = 'Deputy %s (%d)' % (current, value)
        traits = [
            V.delete(),
            V.layer(images, ['Deputy %s (%d)' % (c, value) for c in order],
                    'Change Current', FLIP_KEY, layer_name='Current',
                    description='Deputy current affiliation',
                    start_level=order.index(current) + 1),
            V.marker(['Category', 'Value'], ['Deputy', str(value)]),
            V.basic_piece('', label, gpid),
        ]
        return gpid, V.build_piece(traits), self.size_of(images[0]), label

    def treasury(self, current, amount):
        """Compteur numerique d'assignats : +/- et saisie directe."""
        gpid = self.next_gpid()
        label = 'Treasury %s' % current
        traits = [
            V.labeler('$Amount$', font_size=30, bg='255,255,255',
                      description='Amount in livres'),
            V.dynamic_property('Amount', TREASURY_COMMANDS, value=str(amount),
                               description='Assignats held'),
            V.marker(['Category', 'Current'], ['Treasury', current]),
            V.basic_piece('assignat_50.png', label, gpid),
        ]
        return gpid, V.build_piece(traits), self.size_of('assignat_50.png'), label

    def tracker(self, base, label, category, current, start):
        """Piste ou marqueur de Fame : compteur numerique 1-20, non
        supprimable, chaque changement est journalise (Ok pour les
        trackers)."""
        gpid = self.next_gpid()
        image = base + '.png'
        keys, vals = ['Category'], [C.CATEGORY_LABEL.get(category, category)]
        if current:
            keys.append('Current'); vals.append(current)
        traits = [
            V.report_state(TRACK_KEYS, '$PieceName$: $Value$',
                           description='Report track changes'),
            V.labeler('$Value$', font_size=28, bg='255,255,255',
                      description='Current value'),
            V.dynamic_property('Value', TRACK_COMMANDS, value=str(start),
                               numeric=True, min_value=C.TRACK_MIN,
                               max_value=C.TRACK_MAX, wrap=False,
                               description='Track value (1-20)'),
            V.marker(keys, vals),
            V.basic_piece(image, label, gpid),
        ]
        return gpid, V.build_piece(traits), self.size_of(image)

    def simple(self, base, label, category, current):
        gpid = self.next_gpid()
        image = base + '.png'
        keys, vals = ['Category'], [C.CATEGORY_LABEL.get(category, category)]
        if current:
            keys.append('Current'); vals.append(current)
        traits = [V.delete(), V.marker(keys, vals),
                  V.basic_piece(image, label, gpid)]
        return gpid, V.build_piece(traits), self.size_of(image)

    def secret_note(self):
        """Pion "Secret Note" : masque au clic (visible du seul camp qui l'a
        masque) jusqu'a ce qu'il choisisse de la reveler a tous, texte libre
        editable par le proprietaire."""
        gpid = self.next_gpid()
        label = 'Secret Note'
        image = 'note_blank.png'
        traits = [
            V.hideable(HIDE_KEY, command='Hide/Reveal', bg='0,0,0',
                      access='side:', description='Secret note visibility'),
            V.labeler('Click to edit...', font_size=13, fg='70,55,35',
                      label_key=V.keystroke(69), menu_command='Edit Text',
                      description='Secret note text'),
            V.delete(),
            V.marker(['Category'], ['Note']),
            V.basic_piece(image, label, gpid),
        ]
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
        defs[base] = (gpid, d, size, label, 'personality')

    for base, label, cat, current, _idx in C.PIECES:
        if base in C.TRACKED_PIECES:
            gpid, d, size = b.tracker(base, label, cat, current, C.TRACK_START[base])
        else:
            gpid, d, size = b.simple(base, label, cat, current)
        defs[base] = (gpid, d, size, label, cat)

    for cur in C.CURRENTS:
        for val in C.deputy_values(cur):
            gpid, d, size, label = b.deputy(cur, val)
            defs['depute_%s_%d' % (C.CURRENT_SLUG[cur], val)] = (gpid, d, size, label, 'depute')

    for cur in C.CURRENTS:
        gpid, d, size, label = b.treasury(cur, C.TREASURY[cur])
        defs['tresorerie_' + C.CURRENT_SLUG[cur]] = (gpid, d, size, label, 'treasury')
    gpid, d, size, label = b.treasury('Government', C.TREASURY_GOVERNMENT)
    defs['tresorerie_gouvernement'] = (gpid, d, size, label, 'treasury')

    gpid, d, size = b.secret_note()
    defs['secret_note'] = (gpid, d, size, 'Secret Note', 'note')

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
        panels.append(panel(cur + ' Personalities', bases, cols=3))
    panels.append(panel('Deputies', ['depute_%s_%d' % (C.CURRENT_SLUG[c], v)
                                    for c in C.CURRENTS for v in C.deputy_values(c)], 5))
    panels.append(panel('Control & Revolt', [p[0] for p in C.PIECES if p[2] == 'controle'], 4))
    panels.append(panel('Armies', [p[0] for p in C.PIECES if p[2] == 'armee'], 6))
    panels.append(panel('Track Markers', [p[0] for p in C.PIECES if p[2] == 'piste'], 5))
    panels.append(panel('Treasury', ['assignat_50']
                        + ['tresorerie_' + C.CURRENT_SLUG[c] for c in C.CURRENTS]
                        + ['tresorerie_gouvernement'], 4))
    panels.append(panel('Notes', ['secret_note'], 1))
    palette = ('<VASSAL.build.module.PieceWindow name="Pieces" text="Pieces" '
               'tooltip="Open the pieces palette" hidden="false" scale="1.0" '
               'defaultWidth="0" hotkey="">'
               '<VASSAL.build.widget.TabWidget entryName="Pieces">%s</VASSAL.build.widget.TabWidget>'
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
    board_w, board_h = C.BOARD_PX
    col_w = board_w // len(C.CURRENTS)
    for i, cur in enumerate(C.CURRENTS):
        place('tresorerie_' + C.CURRENT_SLUG[cur],
              i * col_w + col_w - 150, board_h + 200)
    place('tresorerie_gouvernement', board_w // 2, board_h + 430)

    # Assemblee nationale : composition des regles §4.5, en pions de valeur.
    # Les courants non officiellement presents sont dans la MEME pile que
    # leur hote, mais places en dessous (donc visuellement separes) :
    # on les ajoute au tableau `inner` du hote AVANT ses propres pions, de
    # sorte qu'ils se retrouvent au fond de la pile a l'affichage.
    host_extra = {}   # hote -> liste de slots XML a inserer sous sa pile
    for cur, total in C.ASSEMBLY.items():
        host = C.ASSEMBLY_HOST.get(cur)
        if host is None:
            continue
        remaining = total
        extra = []
        for val in sorted(C.deputy_values(cur), reverse=True):
            while remaining >= val:
                gpid, d, size, label, _cat = defs['depute_%s_%d' % (C.CURRENT_SLUG[cur], val)]
                g = b.next_gpid()
                extra.append(slot(label, g, d.replace(';%d;0' % gpid, ';%d;0' % g), size))
                remaining -= val
        host_extra.setdefault(host, []).extend(extra)

    for cur, total in C.ASSEMBLY.items():
        if cur in C.ASSEMBLY_HOST:
            continue   # dissimule dans la pile d'un autre courant, traite ci-dessous
        ax, ay = C.ASSEMBLY_ANCHORS[cur]
        remaining = total
        inner = list(host_extra.get(cur, []))   # dissimules au fond de la pile
        for val in sorted(C.deputy_values(cur), reverse=True):
            while remaining >= val:
                gpid, d, size, label, _cat = defs['depute_%s_%d' % (C.CURRENT_SLUG[cur], val)]
                g = b.next_gpid()
                inner.append(slot(label, g, d.replace(';%d;0' % gpid, ';%d;0' % g), size))
                remaining -= val
        hidden = [h for h, t in C.ASSEMBLY.items() if C.ASSEMBLY_HOST.get(h) == cur]
        name = ('Assembly: %s (%d)' % (cur, total) if not hidden else
                'Assembly: %s (%d) + hidden %s' % (cur, total, ', '.join(hidden)))
        stacks.append(setup_stack(name, ax, ay, ''.join(inner)))

    # ---- carte ----------------------------------------------------------
    map_parts = [
        '<VASSAL.build.module.map.BoardPicker addColumnText="" addRowText="" '
        'boardPrompt="Choose game board" slotHeight="125" slotScale="0.2" slotWidth="350">'
        '<VASSAL.build.module.map.boardPicker.Board image="plan_de_jeu.jpg" name=%s '
        'reversible="false" color="255,255,255" width="0" height="0"/>'
        '</VASSAL.build.module.map.BoardPicker>' % quoteattr(BOARD_NAME),
        '<VASSAL.build.module.map.StackMetrics bottom="8" disabled="false" exSepX="14" '
        'exSepY="20" left="8" right="8" top="8" unexSepX="8" unexSepY="18"/>',
        '<VASSAL.build.module.map.ForwardToKeyBuffer/>',
        '<VASSAL.build.module.map.Scroller/>',
        '<VASSAL.build.module.map.ForwardToChatter/>',
        '<VASSAL.build.module.map.MenuDisplayer/>',
        '<VASSAL.build.module.map.KeyBufferer/>',
        '<VASSAL.build.module.map.PieceMover/>',
        '<VASSAL.build.module.map.HighlightLastMoved/>',
        '<VASSAL.build.module.map.StackExpander/>',
        '<VASSAL.build.module.map.Zoomer zoomLevels="0.4,0.55,0.75,1.0" zoomStart="2"/>',
        '<VASSAL.build.module.map.CounterDetailViewer borderThickness="2" centerAll="false" '
        'delay="300" description="Mouse-over piece viewer" display="true" fgColor="0,0,0" '
        'bgColor="255,255,204" minDisplayPieces="1" showgraph="true" showgraphsingle="true" '
        'showtext="true" zoomlevel="3.0" version="3"/>',
        # ImageSaver en dernier : c'est le seul bouton restant sur la barre
        # d'outils du plateau, place apres les boutons du module principal.
        '<VASSAL.build.module.map.ImageSaver/>',
    ]
    the_map = ('<VASSAL.build.module.Map mapName=%s markMoved="Never" '
               'allowMultiple="false" backgroundcolor="238,230,210" '
               'changeFormat="$message$" color="255,0,0" createFormat="$pieceName$ created in $location$" '
               'edgeHeight="0" edgeWidth="0" hideKey="" highlightThickness="3" '
               'launch="false" moveKey="" moveToFormat="$pieceName$: $previousLocation$ -&gt; $location$" '
               'moveWithinFormat="$pieceName$: $previousLocation$ -&gt; $location$" '
               'onlyReportChangedLocation="false" showKey="" thickness="3" '
               'buttonName="" icon="" tooltip="">%s%s</VASSAL.build.module.Map>'
               % (quoteattr(MAP_NAME), ''.join(map_parts), ''.join(stacks)))

    # ---- fenetre « Charts » : tableaux consultables dans VASSAL ----------
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
    charts = ('<VASSAL.build.module.ChartWindow name="Charts" '
              'text="Charts" tooltip="Reference charts" icon="" hotkey="" description="">'
              '<VASSAL.build.widget.TabWidget entryName="Charts">%s'
              '</VASSAL.build.widget.TabWidget></VASSAL.build.module.ChartWindow>'
              % ''.join(tabs))

    # ---- menu Help : les 11 PDF -------------------------------------------
    docs = ''.join(
        '<VASSAL.build.module.documentation.BrowserPDFFile pdfFile=%s title=%s/>'
        % (quoteattr('pdf/%s.pdf' % name), quoteattr(title))
        for _tail, name, title in C.PDFS)

    roster = ('<VASSAL.build.module.PlayerRoster buttonText="Side" '
              'buttonTooltip="Choose or change side" icon="" buttonKeyStroke="">%s'
              '</VASSAL.build.module.PlayerRoster>'
              % ''.join('<entry>%s</entry>' % escape(c) for c in C.CURRENTS))

    dice = ''.join(
        '<VASSAL.build.module.DiceButton addToTotal="0" hotkey="" icon="" '
        'lockAdd="false" lockDice="false" lockPlus="false" lockSides="false" '
        'nDice="%d" nSides="6" name=%s plus="0" prompt="false" '
        'reportFormat=%s reportTotal="%s" '
        'sortDice="false" text=%s tooltip=%s keepDice="false" keepOption="&gt;" keepCount="1"/>'
        % (n, quoteattr(label),
           quoteattr('** $name$ = ' + (' + '.join('$result%d$' % i for i in range(1, n + 1))
                     + ' = $numericTotal$' if n > 1 else '$result$') + ' ***'),
           'true' if n > 1 else 'false',
           quoteattr(label), quoteattr('Roll ' + label))
        for n, label in ((1, '1d6'), (2, '2d6')))

    # Ordre du menu principal, tel que demande : Side, Pieces, 1d6, 2d6,
    # Inventory, Charts. Le plateau (et son unique bouton restant, Save
    # Image) est declare en dernier.
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<VASSAL.build.GameModule name=%s version=%s description=%s '
        'VassalVersion=%s nextPieceSlotId="%d" ModuleOther1="" ModuleOther2="">'
        # l'encodeur doit venir en premier : sans lui, aucune piece ne se decode
        '<VASSAL.build.module.BasicCommandEncoder/>'
        '<VASSAL.build.module.Documentation>%s</VASSAL.build.module.Documentation>'
        '<VASSAL.build.module.GlobalOptions autoReport="Use Preferences Setting" '
        'centerOnMove="Use Preferences Setting" nonOwnerUnmaskable="Never" '
        'promptString="Choose a side" playerIdFormat="$playerName$" '
        'chatterHTMLSupport="Always"/>'
        '%s'
        '%s'
        '%s'
        '<VASSAL.build.module.Inventory name="Inventory" buttonText="Inventory" '
        'tooltip="List pieces in play" icon="" hotkey="" '
        'groupBy="Category" sortStrategy="Alphabetically" include="{true}" '
        'zoom="1.0" drawPieces="true" foldersOnly="false" showMenu="true" '
        'sides="" centerOnPiece="true" forwardKeystroke="true" '
        'leafFormat="$PieceName$" nonLeafFormat="$PropertyValue$" '
        'label="Pieces in play" launchFunction="functionHide" refreshHotkey="" '
        'sortFormat="$PieceName$" pieceZoom="0.33" pieceZoom2="0.6" pieceZoom3="1.0"/>'
        '%s'
        '%s'
        '</VASSAL.build.GameModule>'
        % (quoteattr(MODULE_NAME), quoteattr(MODULE_VERSION), quoteattr(MODULE_DESC),
           quoteattr(VASSAL_VERSION), b.gpid + 100, docs, roster, palette, dice,
           charts, the_map)
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

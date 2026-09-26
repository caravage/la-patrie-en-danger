# -*- coding: utf-8 -*-
"""Aide de joueur : sequence de jeu (assets/pdf/sequence_of_play_en.pdf). Requiert reportlab."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer

RED = Color(0.9, 0, 0)
BLUE = Color(0, 0, 0.95)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'pdf', 'sequence_of_play_en.pdf')

title = ParagraphStyle('t', fontName='Times-Bold', fontSize=20, leading=24, textColor=RED, spaceAfter=4)
sub = ParagraphStyle('s', fontName='Helvetica-Oblique', fontSize=8.5, textColor=black, spaceAfter=6)
phase = ParagraphStyle('p', fontName='Times-Bold', fontSize=12.5, textColor=RED, spaceBefore=7, spaceAfter=2)
head = ParagraphStyle('h', fontName='Helvetica', fontSize=9, textColor=RED)
step = ParagraphStyle('st', fontName='Helvetica', fontSize=9, textColor=BLUE, leading=11)
tip = ParagraphStyle('tp', fontName='Helvetica', fontSize=7, textColor=BLUE, leading=8.5)
body = ParagraphStyle('b', fontName='Helvetica', fontSize=8.2, leading=10)
rule = ParagraphStyle('r', fontName='Helvetica', fontSize=8, leading=10, textColor=black)

W = A4[0] - 30 * mm
COLS = [W * 0.24, W * 0.66, W * 0.10]


def section(name, rows):
    data = [[Paragraph('Step', head), Paragraph('What happens', head), Paragraph('Rules', head)]]
    for n, (label, hint, text, ref) in enumerate(rows):
        left = [Paragraph(label, step)]
        if hint:
            left.append(Paragraph('&bull; ' + hint, tip))
        data.append([left, Paragraph(text, body), Paragraph(ref, rule)])
    t = Table(data, colWidths=COLS)
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEABOVE', (0, 0), (-1, 0), 1.4, black),
        ('LINEBELOW', (0, 0), (-1, 0), 1.4, black),
        ('LINEBELOW', (0, 1), (-1, -1), 0.4, black),
        ('LINEBEFORE', (1, 0), (1, -1), 0.4, black),
        ('LINEBEFORE', (2, 0), (2, -1), 0.4, black),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return [Paragraph(name, phase), t]


story = [
    Paragraph('Sequence of Play', title),
    Paragraph('One game turn = six months. Eight turns, October 1791 to September 1795. '
              'Each step is completed by the Government, then by every Current in turn order, '
              'before moving on to the next step.', sub),
]
story += section('Initial Phase', [
    ('1. Negotiations', 'Only moment for private talks.',
     'Free discussion, open or private, 10 to 15 minutes. Alliances are never binding. '
     'Currents may give assignats to each other at any time (never to the Government). '
     'The Royalist can never ally with the Mountain or the Sans-Culottes.', '6.1'),
    ('2. Random Events', None,
     'The player controlling the Government rolls 2d6 on each of the four tables of the current regime: '
     'Economy, Politics, Counter-Revolution, Paris Commune, applying the table modifiers '
     '(result kept between 2 and 12). Skip the Commune table while Paris is held by Royalist/Allied armies.', '6.2'),
    ('3. Turn Order', None,
     'Government first. Then Currents by Fame + controlled regions (tie: higher Fame, then a die roll). '
     'Set the markers on the Turn Order track.', '6.3'),
    ('4. Objectives', 'Success +1 Fame, failure -1.',
     'Government, then each Current, declares one precise objective (a target or a region). '
     'A failed Government objective costs -1 to the Government and to its controlling Current.', '6.4'),
    ('5. Personality Placement', None,
     'In turn order, place all your Personalities on regions. You need one in Paris if you control the '
     'Government, one in Paris to persuade deputies, and one in a region to act there.', '6.5'),
])
story += section('Action Phase', [
    ('6. Personality Actions', 'Costs x2 at Economy II, x3 at III.',
     'Arrests (Government), removals (Currents not officially present), then persuasions. '
     'Pay N times the cost for N rolls, keep one (Personality and Regional actions only). '
     'Double 1: Fame -1. Double 6: Fame +1. One action per Personality per turn.', '7.1-7.3'),
    ('7. Regional Actions', None,
     'In this order: plots, then revolts, then revolt suppressions, then Commune raise / suppress. '
     '+2 per influential Personality in the region.', '7.4'),
    ('8. Political Phase', None,
     'Check regime change and elections. Persuade deputies (Legislative, Thermidor, Directorate, '
     'First Republic). King\'s action (Legislative). Propose and vote laws.', '7.5'),
])
story += section("Patriots' Phase", [
    ('9. Justice', None,
     'Judge every imprisoned Personality according to the regime. Trial of Louis XVI is proposed like a law.',
     '8.1, 11.4'),
    ('10. Debates', None,
     'Vote of confidence where the regime allows it (Legislative; Mercy, Directorate, First Republic). '
     'Then return every switched deputy to its original Current.', '8.2-8.3'),
])
story += section('Military Phase', [
    ('11. Reinforcements', 'Unpaid regular army = bankruptcy.',
     'Coalition, then Catholic & Royal armies (placed by the Royalist), then Government. '
     'Maintenance: 100 per army (Economy multiplier applies).', '9.3-9.4'),
    ('12. Movement', None,
     'Coups first (Open scenario). Then Allied, Catholic & Royal, then Revolutionary armies. '
     'Enemy armies may pin revolutionary armies in their region.', '9.5, 12'),
    ('13. Combat', None,
     'One 2d6 roll per contested region on the 13-14 column; the side with more armies attacks '
     '(tie: revolutionary) and adjusts the roll by 1 per extra army. Then military control, kidnapping of the King.',
     '9.6-9.7'),
])
story += section('Interphase', [
    ('14. Economy', 'Spent this turn counter.',
     'Economy +1 per full 1000 assignats spent during the turn. Then set the counter back to 0.', '10.1'),
    ('15. Income', None,
     'Currents: income of controlled regions (minimum 100 + 50 per Personality); the Royalist also gets '
     '50 / 150 / 100 by Coalition level. Government: returns all its money, then receives 2500 minus '
     'regions in revolt, Coalition-held or under a Catholic army (minimum 500).', '10.2'),
    ('16. Fame Adjustment', 'Then advance the Turn marker.',
     'Objectives: +1 if achieved, -1 otherwise. Fled Personalities, placed on the Chronology track, '
     'come back at the start of their turn.', '10.3'),
])

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
                        topMargin=12 * mm, bottomMargin=10 * mm,
                        title='Sequence of Play', author='La patrie en danger - VASSAL module')
doc.build(story)
print(OUT)

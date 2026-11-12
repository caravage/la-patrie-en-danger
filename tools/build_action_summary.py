# -*- coding: utf-8 -*-
"""Aide de joueur : resume des actions (assets/pdf/action_summary_en.pdf). Requiert reportlab."""
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import Color, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle

RED = Color(0.9, 0, 0)
BLUE = Color(0, 0, 0.95)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'pdf', 'action_summary_en.pdf')

title = ParagraphStyle('t', fontName='Times-Bold', fontSize=20, leading=24, textColor=RED, spaceAfter=4)
sub = ParagraphStyle('s', fontName='Helvetica-Oblique', fontSize=8.5, textColor=black, spaceAfter=6)
phase = ParagraphStyle('p', fontName='Times-Bold', fontSize=12, textColor=RED, spaceBefore=5, spaceAfter=3)
head = ParagraphStyle('h', fontName='Helvetica', fontSize=8.5, textColor=RED, leading=10)
step = ParagraphStyle('st', fontName='Helvetica', fontSize=9, textColor=BLUE, leading=11)
tip = ParagraphStyle('tp', fontName='Helvetica', fontSize=7, textColor=BLUE, leading=8.5)
body = ParagraphStyle('b', fontName='Helvetica', fontSize=7.8, leading=9.2)
rule = ParagraphStyle('r', fontName='Helvetica', fontSize=8, leading=10, textColor=black)
note = ParagraphStyle('n', fontName='Helvetica', fontSize=7.8, leading=9.6, spaceBefore=1)

W = landscape(A4)[0] - 24 * mm
COLS = [W * 0.20, W * 0.20, W * 0.20, W * 0.17, W * 0.17, W * 0.06]
HEAD = ['Action', 'Who / cost', 'Personality required?', 'Extra rolls (N &times; cost)?',
        'Uses the Personality\'s action?', 'Rules']


def yes(text):
    return '<b>Yes</b> &ndash; ' + text if text else '<b>Yes</b>'


def no(text):
    return '<b>No</b> &ndash; ' + text if text else '<b>No</b>'


def section(name, rows):
    data = [[Paragraph(h, head) for h in HEAD]]
    for label, hint, who, perso, rolls, used, ref in rows:
        left = [Paragraph(label, step)]
        if hint:
            left.append(Paragraph('&bull; ' + hint, tip))
        data.append([left] + [Paragraph(x, body) for x in (who, perso, rolls, used)] + [Paragraph(ref, rule)])
    t = Table(data, colWidths=COLS, repeatRows=1)
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEABOVE', (0, 0), (-1, 0), 1.4, black),
        ('LINEBELOW', (0, 0), (-1, 0), 1.4, black),
        ('LINEBELOW', (0, 1), (-1, -1), 0.4, black),
        ('LINEBEFORE', (1, 0), (-1, -1), 0.4, black),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return [Paragraph(name, phase), t]


NA = '<b>N/A</b> &ndash; no Personality of yours acts.'

story = [
    Paragraph('Actions Summary', title),
    Paragraph('Who may act, whether a Personality must be on the map, whether several dice rolls may be bought, '
              'and whether the action spends a Personality\'s single action of the turn. '
              'Costs shown are Economy level I: x2 at level II, x3 at level III.', sub),
]
story += section('Personality Actions (step 6)', [
    ('Arrest', 'Resolved first, in turn order.',
     'Government only. 100.',
     no('targets an arrestable Personality of another Current.'),
     yes('declare N and pay before the first roll.'),
     NA, '7.3.1.1'),
    ('Remove (&laquo;arrest&raquo; by a Current)', 'The target leaves the map for one turn.',
     'Currents not officially present in the government, in a region they control. 100.',
     no('targets another Current\'s Personality.'),
     yes('declare N and pay before the first roll.'),
     NA, '7.3.1.2'),
    ('Convince to switch sides', 'After all arrests.',
     'Any Current; the target must bear its symbol (-2 if secondary Current). 100.',
     no('targets another Current\'s Personality.'),
     yes('declare N and pay before the first roll.'),
     NA, '7.3.2'),
])
story += section('Regional Actions (step 7)', [
    ('Plot', 'Gain control of a region.',
     'Any Current. 100. +2 if the region is neutral. Not in a revolting region.',
     yes('one in the region. +2 per influential Personality there (cumulative).'),
     yes('declare N and pay before the first roll.'),
     yes('max. 1 action per Personality per turn.'), '7.4.1'),
    ('Trigger a revolt', None,
     'Currents not officially present only. 150. Not where an army stands.',
     yes('one in the region.'),
     yes('declare N and pay before the first roll.'),
     yes('max. 1 action per Personality per turn.'), '7.4.2'),
    ('Suppress a revolt (Current)', 'A: the Current takes control.',
     'Any Current. 150. Fame -2.',
     yes('one in the region.'),
     yes('declare N and pay before the first roll.'),
     yes('max. 1 action per Personality per turn.'), '7.4.3 b'),
    ('Suppress a revolt (Government)', 'No effect on control.',
     'Government. 150. Fame -2. Not under an Allied or Catholic &amp; Royal army.',
     no(''),
     yes('declare N and pay before the first roll.'),
     NA, '7.4.3 a'),
    ('Raise / suppress the Commune', 'Results depend on the Commune track.',
     'Sans-Culottes, Mountain (-2), Gironde (-4); others under some regimes. 200.',
     yes('one in Paris.'),
     yes('declare N and pay before the first roll.'),
     yes('max. 1 action per Personality per turn.'), '7.4.4'),
])
story += section('Political Actions (step 8)', [
    ('Persuade deputies', 'A: 5 deputies, B: 3. They go back at step 10.',
     'Any Current. 100. Legislative, Thermidor, Directorate, First Republic only.',
     yes('at least one in Paris; each Personality that did no Regional Action may try once.'),
     no('only one dice roll per Political Action.'),
     yes('a Personality that acted in a region cannot persuade.'), '7.5.2.1'),
    ('King\'s action', 'Right after deputies switch.',
     'Current holding the King, Legislative only. Feuillant 100, Royalist 50.',
     no('the King acts.'),
     no('no dice: the effect is automatic.'),
     NA, '7.5.2.2'),
    ('Pass a law', 'One law per Current per turn; same law once per turn.',
     'Currents officially present: 50. Government: free. Who may propose depends on the regime.',
     no(''),
     no('Legislative, Thermidor, Directorate, First Republic: deputies vote, no dice. '
        'Other regimes: a single 2d6 roll on Fame.'),
     NA, '7.5.2.3'),
])
story += [
    Paragraph('Notes', phase),
    Paragraph('&bull; <b>Extra rolls</b>: pay N times the adjusted cost before rolling, roll N times, then keep '
              '<b>one</b> result of your choice (not necessarily the best); the others are ignored, '
              'including their double 1 / double 6 Fame effects. Government actions included.', note),
    Paragraph('&bull; <b>Always one roll</b>: Political Actions, coups d\'&Eacute;tat, kidnapping the King.', note),
    Paragraph('&bull; <b>One action per Personality per turn</b>: a Personality used for a Regional Action '
              'cannot persuade deputies; use another Personality in Paris. '
              'Personality Actions and laws are made by the Current, not by a Personality.', note),
    Paragraph('&bull; <b>Higher is better</b>: modifiers apply to Fame, not to the dice. '
              'In a region under Coalition control, the only action allowed is a Royalist revolt (+2).', note),
]

doc = SimpleDocTemplate(OUT, pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm,
                        topMargin=9 * mm, bottomMargin=8 * mm,
                        title='Actions Summary', author='La patrie en danger - player aid')
doc.build(story)
print(OUT)

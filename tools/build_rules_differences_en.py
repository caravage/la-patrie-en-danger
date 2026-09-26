# -*- coding: utf-8 -*-
"""English version of the rules comparison, written as questions for the
authors of the English rules (assets/pdf/rules_differences_fr_en.pdf).
Requires reportlab."""
import os

from reportlab.lib.colors import Color, black
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

RED = Color(0.9, 0, 0)
BLUE = Color(0, 0, 0.95)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'pdf',
                   'rules_differences_fr_en.pdf')

title = ParagraphStyle('t', fontName='Times-Bold', fontSize=20, leading=24, textColor=RED, spaceAfter=3)
sub = ParagraphStyle('s', fontName='Helvetica-Oblique', fontSize=8.5, leading=11, spaceAfter=6)
phase = ParagraphStyle('p', fontName='Times-Bold', fontSize=13, textColor=RED, spaceBefore=10, spaceAfter=7)
head = ParagraphStyle('h', fontName='Helvetica', fontSize=9, textColor=RED)
label = ParagraphStyle('l', fontName='Helvetica', fontSize=8.3, leading=10.3, textColor=BLUE)
body = ParagraphStyle('b', fontName='Helvetica', fontSize=7.8, leading=9.8)

W = landscape(A4)[0] - 24 * mm
COLS = [W * 0.03, W * 0.14, W * 0.31, W * 0.22, W * 0.30]


def fr(ref, text, quote=None):
    s = '<font color="#0000f2">[%s]</font> %s' % (ref, text)
    if quote:
        s += '<br/><i>« %s »</i>' % quote
    return s


def en(ref, text):
    return '<font color="#0000f2">[%s]</font> %s' % (ref, text)


ROWS = [
    ('1', 'Laws under the Legislative<br/><b>Major</b>',
     fr('XV-A2 p.37, VII-E2 p.17', 'Laws are proposed <b>only by the officially present Currents</b> '
        '(one each, 50 assignats). The Government proposes laws only under the Terror and Thermidor '
        '(and the optional provisional regimes).',
        'proposées par les Tendances, 1 chacune, 50 assignats'),
     en('R.1.3, 7.5.2.3', 'The Government <b>also</b> proposes 1 to 3 laws, at no cost.'),
     'Where does the Government\'s 1-3 laws under the Legislative come from: a designer erratum, '
     'a later edition, or a translation choice?'),
    ('2', 'Government laws (Terror, Thermidor, Wrath, Mercy, Directorate, Prairial)<br/><b>Major</b>',
     fr('VII-E2 p.17', 'The Government <b>must</b> propose <b>1 to 3</b> laws each turn.',
        'Le Gouvernement doit proposer de 1 à 3 Lois par tour de jeu'),
     en('7.5.2.3, R.3.3 and following', '“3 maximum”, with no minimum.'),
     'Was the obligation to propose at least one law dropped on purpose? Under the Terror it decides '
     'whether the Mountain can avoid the two rejected laws that open Thermidor.'),
    ('3', 'Coalition track during foreign war<br/><b>Major</b>',
     fr('IX-B p.21', 'The marker is placed on 20 and <b>stays there until the end of the war</b>, i.e. '
        'until no enemy army is left in France; it may then go down with events and actions. '
        '(XI-B1 p.27 also mentions peace when the marker returns to level I.)',
        'placé sur "20" jusqu\'à la fin de la guerre ; lorsqu\'il n\'y a plus une seule troupe ennemie en France'),
     en('9.2', 'The marker can move <b>only during the Random Events phase</b>; the war ends when no '
        'Allied army is left or when the marker returns to level I.'),
     'Is the marker locked at 20 until no enemy army remains, as in the French text, or can events '
     'lower it during the war?'),
    ('4', 'Coups under the Legislative<br/><b>Major (Historical scenario)</b>',
     fr('XI-C p.27, XV-A5 p.38', 'The whole coup chapter is marked “rule specific to the Open game”, '
        'the Legislative limited coups included.', 'Règle spécifique au jeu "Ouvert"'),
     en('12.0 vs 12.2, R.1.7.1', '12.0 says Open Scenario only, but 12.2 allows the limited coup '
        '“during the Legislative (HS)”.'),
     'Can the Feuillant / Gironde limited coup be used in the Historical scenario?'),
    ('5', 'Number of plotters (popular and limited coups)',
     fr('XI-C p.28', 'One Personality, <b>possibly seconded by one other</b> (+2).',
        'secondée éventuellement par une 2e Personnalité'),
     en('12.1, 12.2', '+2 fame for <b>each</b> additional Personality, no limit.'),
     'Is the number of plotters limited to two?'),
    ('6', 'Successful constitutional referendum',
     fr('XI-D p.29-30', 'The proposing Current <b>and</b> the Government each gain <b>+1 fame</b>. '
        'The referendum is held at the Government\'s request, at the start of the Political phase.',
        'La Tendance et le Gouvernement gagnent chacun +1 point de Renommée'),
     en('R.2.8.3.1, R.3.8.4.1, R.4.8.1.1...', 'No fame gain.'),
     'Was the +1 fame for a successful referendum left out on purpose?'),
    ('7', 'Successful limited coup',
     fr('XI-C4 p.29', 'The Assembly <b>cannot criticise</b> the Government that turn (no vote of confidence).',
        'L\'Assemblée nationale ne peut pas "critiquer" la Tendance au Gouvernement ce tour-ci'),
     en('12.2.2', 'Not mentioned.'),
     'Should the vote of confidence be skipped the turn of a successful limited coup?'),
    ('8', 'King\'s trial under a fame-vote regime (Terror...)',
     fr('XI-A4 p.26', 'The “trial law” must first <b>pass its dice vote</b>; only then do the deputies '
        'vote on the King\'s guilt.', 'si le Gouvernement réussit à proposer la Loi (test de réussite '
        'd\'une Loi nécessaire), un nouveau Procès a lieu'),
     en('11.4', 'The deputies vote on the King\'s guilt as though it were a law.'),
     'Under the Terror, is there a dice test to bring the trial to a vote, then a deputies\' vote?'),
    ('9', 'Marat, Chaumette, Hébert, Roux (and the 4 Royalist generals under the Legislative)',
     fr('XV-A p.37, XV-B p.38, VII-C1 p.13', 'Listed as <b>outlaws</b> (hors-la-loi) in the regime '
        'descriptions, yet the Marat arrest example does not apply the +5.',
        'les Personnalités suivantes sont hors-la-loi : Marat (Mtg), Chaumette (Scu)...'),
     en('R.1.4.1, R.2.4.1...', '“Arrestable (but not outlaws)”.'),
     'Was “arrestable but not outlaws” a deliberate clarification, removing the +5 in Paris and the '
     'automatic arrest at a regime change?'),
    ('10', 'Conscription',
     fr('XII-12 p.32', 'No condition to propose it, and nothing forbids passing it again.'),
     en('13.5.2', 'Only during foreign or civil war, and cannot be passed again until it has ended with peace.'),
     'Where do these two restrictions come from?'),
    ('11', 'Re-elections of a sitting Assembly',
     fr('XI-E p.30', 'Deputies of a Current outlawed in the previous legislature are no longer set aside '
        'but <b>hidden</b> in a close Current (Mountain / Sans-Culotte, Feuillant / Royalist) or in the Marais.',
        'ne sont plus mis de côté, mais placés dans l\'Assemblée "cachés"'),
     en('R.2.6, R.3.6, R.4.6...', 'Not mentioned.'),
     'Should this re-election rule be added?'),
    ('12', 'Combat with equal numbers of armies',
     fr('IX-F p.22', 'Who rolls: 1) the side with more armies; 2) “the Royalist for one, the Government '
        'for the other” (ambiguous).', 'le joueur Royaliste pour l\'un, le joueur au Gouvernement pour l\'autre'),
     en('9.6', 'On a tie, the revolutionary side is the attacker.'),
     'How was the French wording interpreted? Does each side roll?'),
    ('13', 'King\'s action (Legislative)',
     fr('XI-A1 p.25', 'The action <b>is</b> the move of the Coalition marker (1 box), and its consequence '
        'is -1 fame to the Gironde (or to the Feuillant).', 'il peut faire baisser le marqueur des Coalisés '
        'd\'1 case, dans ce cas, la Renommée du Girondin baisse de -1'),
     en('7.5.2.2', 'The fame loss is the action; the Coalition move is <b>optional</b>.'),
     'Is the Coalition move optional?'),
    ('14', 'Fatherland in Danger',
     fr('XII-14 p.32', 'Applies as long as France is in <b>foreign</b> war.',
        'Elle est appliquée tant que la France est en Guerre extérieure'),
     en('13.6', 'Ends with the foreign war or with the civil war, depending on what prompted it.'),
     'Where does the civil-war case come from?'),
    ('15', '5-player game, Marais roll “4”',
     fr('XIV-A p.36', '“Tours controlled” (by the Marais).', '4 : Tours contrôlé'),
     en('15.2.1.1', '“Tours is controlled by the Gironde”.'),
     'Is “by the Gironde” a translation error?'),
    ('16', '5-player game, Government laws',
     fr('XIV-A p.36', 'The Government\'s Current may propose two laws under the <b>Legislative</b> and '
        'the Convention (idem First Republic).', 'deux Lois sous la Législative et la Convention'),
     en('15.2.1.3', 'Two laws under the Convention and the First Republic.'),
     'Should the Legislative be listed?'),
    ('17', 'Outlaws under the First Republic, One & Indivisible',
     fr('VII-C1 p.13 vs XV-K p.51', 'Chapter VII groups this regime with the Terror (Gironde outlawed); '
        'the regime description outlaws only the Royalist and the Feuillant.'),
     en('R.10.4.1', 'Follows the regime description (Royalist and Feuillant).'),
     'Confirm the Gironde is not outlawed (internal contradiction in the French text).'),
    ('18', 'Kidnapped King recaptured',
     fr('XI-A3 p.26 vs XI-A4 NB p.27', 'Trial “immediately” in one place, “the following turn” in another.'),
     en('11.3.1, 11.4', 'Trial the following turn.'),
     'Confirm the following turn (internal contradiction in the French text).'),
]

CHART_ROWS = [
    ('Freedom of Religion', 'Commune <b>-2</b> in the French rulebook (XII-9 p.31) and in the English '
     'rules (13.3.3); the English “The Laws” chart says -1.'),
    ('Declaration of War, Conscription', 'No “once per game” restriction in the French rulebook '
     '(XII-11, XII-12 p.32); the English “The Laws” chart adds it to both.'),
]


def table(data, cols):
    t = Table(data, colWidths=cols, repeatRows=1)
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEABOVE', (0, 0), (-1, 0), 1.4, black),
        ('LINEBELOW', (0, 0), (-1, 0), 1.4, black),
        ('LINEBELOW', (0, 1), (-1, -1), 0.4, black),
        ('LINEBEFORE', (1, 0), (-1, -1), 0.4, black),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return t


story = [
    Paragraph('French 1995 Rulebook vs. English Rules', title),
    Paragraph('Comparison of the official Azure Wish rulebook (French, 1995) with the English “Decimal '
              'Version 1.0” edited by MWBigney. French references are section and page of the 1995 '
              'rulebook; original French wording is quoted in italics. Everything else matches: set-up, '
              'Result Table, action costs and effects, regime change conditions, election formulas, '
              'victory points and final rankings.', sub),
]
data = [[Paragraph(h, head) for h in ('#', 'Topic', 'French rulebook (1995)', 'English rules', 'Question')]]
for n, topic, f, e, q in ROWS:
    data.append([Paragraph(n, body), Paragraph(topic, label), Paragraph(f, body), Paragraph(e, body),
                 Paragraph(q, body)])
story.append(table(data, COLS))
story.append(Paragraph('English player aids contradicted by the French rulebook', phase))
data = [[Paragraph('Law', head), Paragraph('Finding', head)]]
for s, txt in CHART_ROWS:
    data.append([Paragraph(s, label), Paragraph(txt, body)])
story.append(table(data, [W * 0.22, W * 0.78]))

doc = SimpleDocTemplate(OUT, pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm,
                        topMargin=10 * mm, bottomMargin=10 * mm,
                        title='French vs English rules', author='La patrie en danger - VASSAL module')
doc.build(story)
print(os.path.normpath(OUT))

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
COLS = [W * 0.03, W * 0.12, W * 0.07, W * 0.27, W * 0.20, W * 0.21, W * 0.10]

# scenario concerned by each row (Historical, Open or both)
SCEN = {'1': 'Both', '2': 'Both', '3': 'Both', '4': 'Historical', '5': 'Open', '6': 'Open', '7': 'Open',
        '8': 'Both', '9': 'Both', '10': 'Both', '11': 'Both', '12': 'Both', '13': 'Both', '14': 'Both',
        '15': 'Both', '16': 'Both', '17': 'Open', '18': 'Both'}


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
    ('5', 'Number of plotters (popular, limited and military coups)',
     fr('XI-C p.28, XI-C3 p.28', 'One Personality, <b>possibly seconded by one other</b> (+2); same for '
        'the rally of a military coup.', 'secondée éventuellement par une 2e Personnalité'),
     en('12.1, 12.2, 12.3.1', '+2 fame for <b>each</b> additional Personality, no limit.'),
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
     '<b>Resolved by the designers</b> (Marcé, Goyon; errata XI-B2): the +5 applies only to outlawed '
     'factions, not to these leaders. The English rules are correct.'),
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
ROWS += [
    ('19', 'Military coup: failed rally',
     fr('XI-C3 p.28', 'The plotting Personalities “immediately become outlaws” when the rally is attempted; '
        'if the rally fails, only the Current and the Personalities that did not take part escape outlaw status.',
        'Ces Personnalités deviennent immédiatement hors-la-loi. [...] Si le ralliement échoue, la Tendance et '
        'les Personnalités n\'ayant pas participé au coup d\'Etat ne sont pas considérées hors-la-loi'),
     en('12.3.1', '“If the rally attempt fails, nothing happens”; the Personalities are outlawed only if '
        'the rally succeeds.'),
     'Are the plotters outlawed even when the rally fails?'),
    ('20', 'Military coup: time of the combat in Paris',
     fr('XI-C3 p.29', 'The combat takes place at the <b>end of the Movement segment</b>.',
        'Le combat a exceptionnellement lieu à la fin de la s/phase de Mouvement'),
     en('12.3.3', 'Resolved at the end of the <b>intercepting armies\'</b> movement.'),
     'Is the combat fought before or after the other armies move?'),
    ('21', 'Failed popular or military coup: the Commune',
     fr('XI-C4 p.29', 'The plotting Current <b>loses control of the Commune</b>, which becomes neutral.',
        'La Tendance perd éventuellement le contrôle de la Commune (qui redevient neutre)'),
     en('12.1.1, 12.3.3.1', 'Not in the general rule; only some regime descriptions say so '
        '(R.3.7.2.2, R.4.7.2.1, R.6.7.2.1...).'),
     'Does the loss of the Commune apply to every failed popular or military coup?'),
    ('22', 'Legislative: Gironde popular coup',
     fr('XV-A5 p.38', 'The Gironde may attempt a limited <b>or popular</b> coup only if the Feuillant has '
        'previously succeeded a limited coup against it, or if the Commune is at level III.',
        'le Girondin peut tenter un coup d\'Etat limité/populaire contre le Feuillant si ce dernier a '
        'précédemment réussi un coup d\'Etat limité contre lui ou si la Commune est en seuil III'),
     en('R.1.7.1.2, R.1.7.2.1', 'The condition applies to the limited coup only; the popular coup has no '
        'precondition.'),
     'Does the condition also restrict the Gironde\'s popular coup?'),
    ('23', 'Legislative to Convention / Terror: “12+ regions”',
     fr('XV-A6 p.38', '12 or more regions controlled by the Royalist and the Coalition; no double count.',
        'si 12+ régions sont contrôlées par le Royaliste et les Coalisés'),
     en('R.1.8.1, R.1.8.2', 'A region controlled by both the Royalist and the Coalition <b>counts twice</b>.'),
     'Where does the double count come from?'),
    ('24', 'Coups to Prairial: who controls the Commune',
     fr('XV-D4 p.43, XV-G5 p.48', 'Thermidor: Commune at level III “(Mtg or Scu)”; Directorate: level II '
        '(Scu) or III (Scu, Mtg). Either Current may plot with the other\'s Commune, which must agree (XI-C1).',
        'la Commune doit être soulevée et en seuil III (Mtg ou Scu)'),
     en('R.4.7.2.1-2, R.7.7.2.1-2', 'The Commune must be controlled by the plotting Current.'),
     'May the Mountain plot with a Sans-Culotte Commune (and vice versa)?'),
    ('25', 'Directorate: number of coups to Prairial',
     fr('XV-G5 NB p.48', '<b>Only one</b> attempt: if the Mountain tries, neither it nor the Sans-Culotte '
        'may try again.', 'il ne peut y avoir qu\'une seule tentative de coup d\'Etat'),
     en('R.7.7.2', 'Only the Royalist is limited to one attempt.'),
     'Was the single attempt for the Mountain / Sans-Culotte dropped on purpose?'),
    ('26', 'Directorate: running the two-headed Government',
     fr('XV-G3 p.47-48', 'Silent on the first partner and on how a new partner is chosen after a vote of '
        'no confidence; on a disagreement, only “the Current not in power (Gironde or Feuillant)” may give +2; '
        'no special timing for limited coups.',
        'La Tendance qui n\'est pas au pouvoir (entre le Girondin et le Feuillant) peut accorder un bonus de +2'),
     en('R.7.2, R.7.2.2, R.7.5, R.7.7.1', 'First partner: most deputies (Marais breaks ties); the Mountain may '
        'also give +2; re-roll ties; new partner chosen by a second Assembly vote without the old partner; '
        'limited coups just before the Political Actions.'),
     'Are these additions designer clarifications?'),
    ('27', 'Mercy to Directorate: time of the referendum',
     fr('XI-D p.29, XV-F p.45', 'Referendums are held at the Government\'s request at the <b>start of the '
        'Political phase</b>; the new regime applies immediately.',
        'Ceci se joue, à la demande du Gouvernement, au début de la phase d\'Action politique'),
     en('R.6.8.2', 'Held at the <b>end of the turn</b>; the Directorate is installed at the next Political phase.'),
     'Start of the Political phase, or end of the turn?'),
    ('28', 'First Republic, One & Indivisible: Sans-Culotte variant',
     fr('XV-K3 p.52', '<b>Marat switches to the Sans-Culotte</b> and can no longer be switched back by the Mountain.',
        'Marat passe au Sans-culotte et ne peut plus être "retourné" par le Montagnard'),
     en('R.10.9.4', 'Not mentioned.'),
     'Should Marat\'s switch be added?'),
    ('29', 'Elections when the Terror is installed',
     fr('XV-C1 p.40', 'Same Assembly after the Convention, new elections after the Federal Republic; '
        'Mountain deputies set aside after a failed coup are reinstated. Nothing for Legislative to Terror.'),
     en('R.3.6', 'New elections also after the Legislative; no reinstatement of Mountain deputies.'),
     'Confirm the Legislative case and the reinstatement of Mountain deputies.'),
    ('30', 'Outlaws under Prairial',
     fr('VII-C1 p.13 vs XV-H p.48', 'Chapter VII groups Prairial with the Terror (Royalist, Gironde, Feuillant); '
        'the regime description also outlaws the <b>Marais</b>.'),
     en('R.8.4.1', 'Follows the regime description (Marais outlawed).'),
     'Confirm the Marais is outlawed (internal contradiction in the French text).'),
    ('31', 'Directorate: revolutionary majority at the end',
     fr('XIII-C4 NB p.35', 'The Mountain wins instead of the Gironde only if it is <b>not outlawed</b> and '
        'has more VP.', 'si le Montagnard n\'est pas hors-la-loi, il peut gagner'),
     en('14.3.5', 'Gironde or Mountain by VP, Gironde wins ties; no outlaw condition.'),
     'Should an outlawed Mountain be unable to win?'),
    ('32', 'Ties for the winner',
     fr('XIII-C p.35', 'No tie rule.'),
     en('14.3.1 to 14.3.5', 'Feuillant beats Marais; Mountain beats Gironde (Convention) and Sans-Culotte '
        '(Terror); Gironde beats Mountain (Directorate).'),
     'Do these tie-breakers come from the designers?'),
]
for n in range(19, 33):
    SCEN[str(n)] = 'Open'
SCEN['23'] = SCEN['29'] = SCEN['32'] = 'Both'

# text we follow: French where it is explicit, English (or the designers) where the French text is
# ambiguous or self-contradictory, English additions where the French text is silent
F, E = '<b>French</b>', '<b>English</b>'
VERDICT = {
    '1': F, '2': F, '3': F + '<br/>(to confirm, see XI-B1)', '4': F, '5': F, '6': F, '7': F, '8': F,
    '9': E + '<br/>(designers)', '10': '<b>Designers</b>: once only, no war condition', '11': F, '12': E + '<br/>(French ambiguous)',
    '13': F, '14': F, '15': F, '16': F, '17': E + '<br/>(regime description)', '18': E + '<br/>(French contradictory)',
    '19': E + '<br/>(French ambiguous)', '20': F, '21': F, '22': F, '23': E + '<br/>(French silent)', '24': F, '25': F,
    '26': F + ' for the +2 bonus; ' + E + ' for the rest (French silent)', '27': F, '28': F,
    '29': E + ' for Legislative; ' + F + ' for the Mountain deputies', '30': E + '<br/>(regime description)',
    '31': F, '32': E + '<br/>(French silent)',
}

CHART_ROWS = [
    ('Freedom of Religion', 'Commune <b>-2</b> in the French rulebook (XII-9 p.31) and in the English '
     'rules (13.3.3); the English “The Laws” chart says -1.'),
    ('Declaration of War, Conscription', 'Not in the French rulebook (XII-11, XII-12 p.32), but <b>the '
     'designers</b> (Marcé; errata VII-E2) state that War, Fatherland in Danger and Conscription can be '
     'passed only once: the English “The Laws” chart is right.'),
]


XREFS = [
    ('1.1', 'Victory “is determined in a three-step process outlined in 15.0”.', '14.0'),
    ('11.4', 'Second trial: “Thermidor (HS) or Mercy (HS)”.', 'Mercy (OS)'),
    ('14.3.5', '“consult 15.4 as though the Terror had been in place”.', '14.4'),
    ('15.2.2', 'Marais “controlled by the game system, exactly as 15.3.1”.', '15.2.1'),
    ('R.2.1', 'Convention brought about by a Gironde coup “(see R.1.7.1 and R.1.7.3)”.', 'R.1.7.2 and R.1.7.3'),
    ('R.4.8.2', 'Thermidor to Prairial “By Montagne (R.5.7.2.1) or Sans-Culotte (R.5.7.2.2)”.',
     'R.4.7.2.1 and R.4.7.2.2'),
    ('R.7.7.3.1', '“applied immediately (see XI-C4)”: French rulebook numbering.', '12.3.3.2'),
    ('R.10.1.1', '“All outlaw personalities (R.9.4.1)”.', 'R.10.4.1'),
    ('R.10.1.2', '“Montagne Variant (see 10.9.3) or the Sans-Culotte Variant (see 10.9.4)”.', 'R.10.9.3, R.10.9.4'),
    ('R.10.7.2', 'Number used twice (Switching Variants, then Popular Coups).', 'R.10.7.2 and R.10.7.3 (then R.10.7.4)'),
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
              'Version 1.0” edited by MWBigney, Historical and Open scenarios. French references are section '
              'and page of the 1995 rulebook; original French wording is quoted in italics. Everything else '
              'matches, including all eleven regime descriptions: set-up, Result Table, action costs and '
              'effects, regime change conditions, election formulas, victory points and final rankings. '
              '<b>Verdict</b>: the text we play by. The French rulebook prevails where it is explicit; the '
              'English rules (or the designers\' answers) where the French text is ambiguous or contradicts '
              'itself; the English additions where the French text is silent.', sub),
]
data = [[Paragraph(h, head) for h in ('#', 'Topic', 'Scenario', 'French rulebook (1995)', 'English rules',
                                      'Question', 'Verdict')]]
for n, topic, f, e, q in ROWS:
    data.append([Paragraph(n, body), Paragraph(topic, label), Paragraph(SCEN[n], body), Paragraph(f, body),
                 Paragraph(e, body), Paragraph(q, body), Paragraph(VERDICT[n], body)])
story.append(table(data, COLS))
story.append(Paragraph('English player aids checked against the French rulebook', phase))
data = [[Paragraph('Law', head), Paragraph('Finding', head)]]
for s, txt in CHART_ROWS:
    data.append([Paragraph(s, label), Paragraph(txt, body)])
story.append(table(data, [W * 0.22, W * 0.78]))
story.append(Paragraph('Cross-reference errors in the English rules', phase))
data = [[Paragraph('Section', head), Paragraph('Text', head), Paragraph('Should read', head)]]
for sec, txt, fix in XREFS:
    data.append([Paragraph(sec, label), Paragraph(txt, body), Paragraph(fix, body)])
story.append(table(data, [W * 0.12, W * 0.55, W * 0.33]))
story.append(Paragraph('<br/>Also in the English rules only: optional rule 15.3 “Ever-So-Slightly More Fair '
                       'Euro-ish Variant” (proposed by HSGC/NYNA players), not part of the 1995 rulebook.', sub))

doc = SimpleDocTemplate(OUT, pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm,
                        topMargin=10 * mm, bottomMargin=10 * mm,
                        title='French vs English rules', author='La patrie en danger - VASSAL module')
doc.build(story)
print(os.path.normpath(OUT))

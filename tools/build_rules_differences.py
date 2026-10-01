# -*- coding: utf-8 -*-
"""Tableau des differences entre le livret francais de 1995 et les regles
anglaises (assets/pdf/differences_regles_fr_en.pdf). Requiert reportlab."""
import os

from reportlab.lib.colors import Color, black
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

RED = Color(0.9, 0, 0)
BLUE = Color(0, 0, 0.95)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'pdf',
                   'differences_regles_fr_en.pdf')

title = ParagraphStyle('t', fontName='Times-Bold', fontSize=20, leading=24, textColor=RED, spaceAfter=3)
sub = ParagraphStyle('s', fontName='Helvetica-Oblique', fontSize=8.5, leading=11, spaceAfter=6)
phase = ParagraphStyle('p', fontName='Times-Bold', fontSize=13, textColor=RED, spaceBefore=10, spaceAfter=7)
head = ParagraphStyle('h', fontName='Helvetica', fontSize=9, textColor=RED)
label = ParagraphStyle('l', fontName='Helvetica', fontSize=8.5, leading=10.5, textColor=BLUE)
body = ParagraphStyle('b', fontName='Helvetica', fontSize=8, leading=10)
impact = ParagraphStyle('i', fontName='Helvetica-Bold', fontSize=8, leading=10)

W = landscape(A4)[0] - 24 * mm
COLS = [W * 0.03, W * 0.15, W * 0.07, W * 0.28, W * 0.24, W * 0.23]

# scénario concerné : Historique, Ouvert ou les deux
SCEN = {str(n): 'Les deux' for n in range(1, 33)}
for n in (5, 6, 7, 17, 19, 20, 21, 22, 24, 25, 26, 27, 28, 30, 31):
    SCEN[str(n)] = 'Ouvert'
SCEN['4'] = 'Historique'

ROWS = [
    ('1', 'Lois sous la Législative',
     'Proposées <b>uniquement par les courants</b> officiellement présents (1 chacun, 50 assignats).',
     'Le Gouvernement en propose <b>aussi</b> 1 à 3, gratuitement.',
     '<b>Fort.</b>'),
    ('2', 'Lois du Gouvernement (Terreur, Thermidor, Épouvante, Indulgence, Directoire, Prairial)',
     'Le Gouvernement <b>doit</b> proposer <b>1 à 3</b> lois par tour.',
     '« 3 maximum », sans obligation.',
     '<b>Fort</b> : sous la Terreur, la Montagne ne peut pas éviter les rejets qui ouvrent Thermidor.'),
    ('3', 'Piste Coalisés pendant la guerre',
     '<b>Bloquée à 20</b> tant qu\'il reste une armée ennemie en France.',
     'Ne bouge que par les événements ; la paix survient si elle retombe au niveau I.',
     '<b>Fort.</b>'),
    ('4', 'Coups d\'État sous la Législative',
     'Tout le chapitre est réservé au scénario <b>Ouvert</b>.',
     '12.2 autorise le coup limité sous la Législative en scénario Historique.',
     '<b>Fort</b> en scénario Historique.'),
    ('5', 'Nombre de conjurés (coups populaire, limité et militaire)',
     '1 personnalité + <b>au plus 1</b> seconde (+2), y compris pour rallier une armée.',
     '+2 <b>par</b> personnalité supplémentaire, sans limite.',
     'Moyen.'),
    ('6', 'Référendum réussi',
     'Le courant proposant et le Gouvernement gagnent <b>+1 Renommée</b> ; le référendum a lieu '
     'à la demande du Gouvernement.',
     'Pas de gain de Renommée.',
     'Moyen.'),
    ('7', 'Coup limité réussi',
     '<b>Pas de vote de confiance</b> ce tour-là.',
     'Rien de prévu.',
     'Moyen.'),
    ('8', 'Procès du Roi sous un régime à vote par Renommée (Terreur...)',
     'La « loi » procès doit d\'abord <b>réussir son jet</b>, puis les députés votent.',
     'Les députés votent directement.',
     'Moyen.'),
    ('9', 'Marat, Chaumette, Hébert, Roux (et les 4 généraux royalistes sous la Législative)',
     'Qualifiés de « <b>hors-la-loi</b> » dans les fiches de régime, mais l\'exemple d\'arrestation '
     'n\'applique pas le +5.',
     '« Arrestable (but not outlaws) ».',
     '<b>Résolu par les auteurs</b> (Marcé, Goyon ; errata XI-B2) : le +5 ne vaut que pour les '
     'courants hors-la-loi, pas pour ces personnalités. La VO est correcte.'),
    ('10', 'Conscription',
     'Aucune condition.',
     'Seulement en guerre, et non revotable avant la paix.',
     'Moyen : ajout de la VO.'),
    ('11', 'Réélections',
     'Les députés d\'un courant hors-la-loi ne sont plus mis de côté mais <b>cachés</b> dans un '
     'courant proche ou dans le Marais.',
     'Absent.',
     'Faible.'),
    ('12', 'Combat à égalité d\'armées',
     '« Le Royaliste pour l\'un, le Gouvernement pour l\'autre » (ambigu).',
     'L\'attaquant est le camp révolutionnaire.',
     'Faible.'),
    ('13', 'Action du Roi',
     'Le déplacement de la piste Coalisés fait <b>partie</b> de l\'action.',
     'Déplacement optionnel.',
     'Faible.'),
    ('14', 'Patrie en danger',
     'Active tant que dure la guerre <b>extérieure</b>.',
     'Également pendant la guerre civile (armée catholique).',
     'Faible.'),
    ('15', 'Jeu à 5, jet du Marais n° 4',
     '« Tours contrôlé » (sous-entendu par le Marais).',
     '« Tours contrôlé par la <b>Gironde</b> ».',
     'Faible : erreur de la VO.'),
    ('16', 'Jeu à 5, lois du Gouvernement',
     '2 lois sous la <b>Législative</b> et la Convention.',
     '2 lois sous la Convention et la <b>1re République</b>.',
     'Faible.'),
    ('17', 'Hors-la-loi sous la 1re République Une & Indivisible',
     'Le chapitre VII range ce régime avec la Terreur (Girondin hors-la-loi) ; la fiche du régime '
     'dit Royaliste et Feuillant seulement.',
     'Suit la fiche du régime.',
     'Incohérence interne de la VF.'),
    ('18', 'Roi enlevé puis repris',
     'Procès « immédiat » (XI-A3) ou « au tour suivant » (NB), selon le passage.',
     'Tour suivant.',
     'Incohérence interne de la VF.'),
    ('19', 'Coup militaire : ralliement raté',
     'Les conjurés « deviennent immédiatement hors-la-loi » ; si le ralliement échoue, seuls la Tendance '
     'et les non-participants y échappent (XI-C3).',
     '« Si le ralliement échoue, rien ne se passe » ; hors-la-loi seulement en cas de réussite (12.3.1).',
     'Moyen.'),
    ('20', 'Coup militaire : moment du combat à Paris',
     'À la <b>fin de la sous-phase de Mouvement</b> (XI-C3).',
     'Juste après le mouvement des armées d\'interception (12.3.3).',
     'Faible.'),
    ('21', 'Coup populaire ou militaire raté : la Commune',
     'La Tendance <b>perd le contrôle de la Commune</b>, qui redevient neutre (XI-C4).',
     'Absent de la règle générale ; seulement dans certaines fiches de régime.',
     'Faible.'),
    ('22', 'Législative : coup populaire de la Gironde',
     'Coup limité <b>ou populaire</b> seulement si le Feuillant a déjà réussi un coup limité contre elle, '
     'ou si la Commune est en seuil III (XV-A5).',
     'La condition ne vise que le coup limité ; le coup populaire n\'a pas de condition (R.1.7.2.1).',
     'Moyen.'),
    ('23', 'Législative vers Convention / Terreur : « 12+ régions »',
     'Régions contrôlées par le Royaliste et les Coalisés, sans double compte (XV-A6).',
     'Une région contrôlée par les deux <b>compte double</b> (R.1.8).',
     'Faible.'),
    ('24', 'Coups vers Prairial : qui tient la Commune',
     'Sous Thermidor : seuil III « (Mtg ou Scu) » ; sous le Directoire : seuil II (Scu) ou III (Scu, Mtg). '
     'L\'un peut comploter avec la Commune de l\'autre, qui doit donner son accord (XV-D4, G5, XI-C1).',
     'La Commune doit être contrôlée par la Tendance qui complote (R.4.7.2, R.7.7.2).',
     'Faible.'),
    ('25', 'Directoire : nombre de coups vers Prairial',
     '<b>Une seule</b> tentative : si la Montagne essaie, ni elle ni le Sans-Culotte ne peuvent '
     'recommencer (XV-G5 NB).',
     'Seul le Royaliste est limité à une tentative.',
     'Moyen.'),
    ('26', 'Directoire : fonctionnement du Gouvernement à deux têtes',
     'Rien sur le premier partenaire ni sur le choix d\'un nouveau partenaire après une défiance ; en cas de '
     'désaccord, seule « la Tendance qui n\'est pas au pouvoir (Girondin ou Feuillant) » donne +2 (XV-G3).',
     'Premier partenaire : le plus de députés ; la Montagne peut aussi donner +2 ; nouveau partenaire élu par '
     'un second vote ; coups limités juste avant les Actions politiques (R.7.2, R.7.5, R.7.7.1).',
     'Faible : ajouts de la VO.'),
    ('27', 'Indulgence vers Directoire : moment du référendum',
     'Au <b>début de la phase d\'Action politique</b>, à la demande du Gouvernement (XI-D).',
     'À la <b>fin du tour</b> ; Directoire installé à la phase politique suivante (R.6.8.2).',
     'Faible.'),
    ('28', '1re République Une &amp; Indivisible, variante Sans-Culotte',
     '<b>Marat passe au Sans-Culotte</b> et ne peut plus être retourné par la Montagne (XV-K3).',
     'Absent (R.10.9.4).',
     'Faible.'),
    ('29', 'Élections à l\'installation de la Terreur',
     'Même Assemblée après la Convention, élections après la République fédérale ; les députés montagnards '
     'écartés après un coup raté sont réhabilités. Rien pour Législative vers Terreur (XV-C1).',
     'Élections aussi après la Législative ; pas de réhabilitation des députés montagnards (R.3.6).',
     'Faible.'),
    ('30', 'Hors-la-loi sous Prairial',
     'Le chapitre VII range Prairial avec la Terreur (Royaliste, Girondin, Feuillant) ; la fiche du régime '
     'met aussi le <b>Marais</b> hors-la-loi.',
     'Suit la fiche du régime.',
     'Incohérence interne de la VF.'),
    ('31', 'Directoire : majorité révolutionnaire en fin de partie',
     'La Montagne ne gagne à la place de la Gironde que si elle n\'est <b>pas hors-la-loi</b> (XIII-C4 NB).',
     'Gironde ou Montagne aux PV, la Gironde gagne les égalités ; pas de condition (14.3.5).',
     'Faible.'),
    ('32', 'Égalités pour désigner le vainqueur',
     'Aucune règle (XIII-C).',
     'Feuillant devant Marais, Montagne devant Gironde (Convention) et Sans-Culotte (Terreur), Gironde '
     'devant Montagne (Directoire) (14.3).',
     'Faible : ajout de la VO.'),
]

XREFS = [
    ('1.1', '« outlined in 15.0 »', '14.0'),
    ('11.4', '« Mercy (HS) »', 'Mercy (OS)'),
    ('14.3.5', '« consult 15.4 »', '14.4'),
    ('15.2.2', '« exactly as 15.3.1 »', '15.2.1'),
    ('R.2.1', '« see R.1.7.1 and R.1.7.3 »', 'R.1.7.2 et R.1.7.3'),
    ('R.4.8.2', '« (R.5.7.2.1) … (R.5.7.2.2) »', 'R.4.7.2.1 et R.4.7.2.2'),
    ('R.7.7.3.1', '« see XI-C4 » (numérotation française)', '12.3.3.2'),
    ('R.10.1.1', '« (R.9.4.1) »', 'R.10.4.1'),
    ('R.10.1.2', '« see 10.9.3 / 10.9.4 »', 'R.10.9.3, R.10.9.4'),
    ('R.10.7.2', 'Numéro utilisé deux fois', 'R.10.7.2 puis R.10.7.3'),
]

CHART_ROWS = [
    ('Freedom of Religion (Libertés du Culte)',
     'Commune <b>-2</b> dans la VF et dans les règles anglaises ; l\'aide « The Laws » indique à tort -1.'),
    ('Déclaration de guerre, Conscription',
     'La VF ne le dit pas, mais <b>les auteurs</b> (Marcé ; errata VII-E2) précisent que Déclaration de guerre, '
     'Patrie en danger et Conscription ne peuvent être adoptées qu\'une fois : l\'aide « The Laws » est fondée.'),
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
    Paragraph('Règles françaises (1995) et règles anglaises', title),
    Paragraph('Comparaison du livret officiel Azure Wish (1995) avec la « Decimal Version 1.0 » anglaise '
              '(MWBigney), scénarios Historique et Ouvert. Identiques par ailleurs, y compris les onze fiches '
              'de régime : mise en place, table de résolution, coûts et effets des actions, conditions de '
              'passage entre régimes, formules d\'élection, points de victoire et classements.', sub),
]
data = [[Paragraph(h, head) for h in ('#', 'Sujet', 'Scénario', 'VF 1995 (officielle)', 'Règles anglaises',
                                      'Impact')]]
for n, s, fr, en, imp in ROWS:
    data.append([Paragraph(n, body), Paragraph(s, label), Paragraph(SCEN[n], body), Paragraph(fr, body),
                 Paragraph(en, body), Paragraph(imp, body)])
story.append(table(data, COLS))
story.append(Paragraph('Aides de jeu anglaises vérifiées sur la VF', phase))
data = [[Paragraph('Loi', head), Paragraph('Constat', head)]]
for s, txt in CHART_ROWS:
    data.append([Paragraph(s, label), Paragraph(txt, body)])
story.append(table(data, [W * 0.25, W * 0.75]))
story.append(Paragraph('Renvois erronés dans les règles anglaises', phase))
data = [[Paragraph('Section', head), Paragraph('Texte', head), Paragraph('Lire', head)]]
for sec, txt, fix in XREFS:
    data.append([Paragraph(sec, label), Paragraph(txt, body), Paragraph(fix, body)])
story.append(table(data, [W * 0.15, W * 0.5, W * 0.35]))
story.append(Paragraph('<br/>Également propre aux règles anglaises : la règle optionnelle 15.3 « Ever-So-Slightly '
                       'More Fair Euro-ish Variant », proposée par des joueurs, absente du livret de 1995.', sub))

doc = SimpleDocTemplate(OUT, pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm,
                        topMargin=10 * mm, bottomMargin=10 * mm,
                        title='Différences règles FR / EN', author='La patrie en danger - VASSAL module')
doc.build(story)
print(os.path.normpath(OUT))

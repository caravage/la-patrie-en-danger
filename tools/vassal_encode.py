# -*- coding: utf-8 -*-
"""Encodage des pieces VASSAL.

Portage fidele de VASSAL.tools.SequenceEncoder et des methodes myGetType()/
myGetState() des traits utilises. Les regles ont ete verifiees directement dans
les sources de VASSAL (vassal-app/src/main/java/VASSAL).

Point critique : Decorator.getType() fait
    new SequenceEncoder(myGetType(), '\t').append(piece.getType())
ce qui **echappe** les tabulations deja presentes dans la chaine interieure.
Sans cet echappement, VASSAL ne sait plus decouper la chaine et perd tous les
traits au-dela du deuxieme, ainsi que l'image et le nom de la piece.
"""

CTRL = 130  # InputEvent.CTRL_MASK | CTRL_DOWN_MASK, tel que VASSAL le serialise


class SequenceEncoder:
    """Equivalent de VASSAL.tools.SequenceEncoder."""

    def __init__(self, delimiter, first=None):
        self.delim = delimiter
        self.buf = None
        if first is not None:
            self.append(first)

    def _escape(self, s):
        return ''.join('\\' + c if c == self.delim else c for c in s)

    def append(self, value):
        if value is None:
            value = ''
        elif value is True:
            value = 'true'
        elif value is False:
            value = 'false'
        else:
            value = str(value)

        if self.buf is None:
            self.buf = []
        else:
            self.buf.append(self.delim)

        if value == '':
            return self
        # VASSAL protege les chaines commencant par \ ou entierement quotees
        if value[0] == '\\' or (value[0] == "'" and value[-1] == "'"):
            self.buf.append("'" + self._escape(value) + "'")
        else:
            self.buf.append(self._escape(value))
        return self

    def value(self):
        return '' if self.buf is None else ''.join(self.buf)


def seq(delimiter, *values):
    e = SequenceEncoder(delimiter)
    for v in values:
        e.append(v)
    return e.value()


def string_array(items):
    """StringArrayConfigurer.arrayToString : elements joints par ',' echappes."""
    if not items:
        return ''
    return seq(',', *items)


def keystroke(code, modifiers=CTRL):
    """HotKeyConfigurer.encode : '<keycode>,<modifiers>'."""
    return '%d,%d' % (code, modifiers)


# --- Traits -----------------------------------------------------------------

class Trait:
    """Un trait (Decorator) : une paire type/etat."""

    def __init__(self, type_string, state_string=''):
        self.type = type_string
        self.state = state_string


def basic_piece(image, name, gpid):
    """BasicPiece : le coeur de la piece. type 'piece;<clone>;<delete>;<img>;<nom>'."""
    return Trait(
        'piece;' + seq(';', '', '', image or '', name or ''),
        seq(';', 'null', 0, 0, gpid, 0),
    )


def delete(command='Delete', key=keystroke(68)):        # Ctrl+D
    return Trait('delete;' + seq(';', command, key, ''), '')


def clone(command='Clone', key=keystroke(75)):         # Ctrl+K
    return Trait('clone;' + seq(';', command, key, ''), '')


def marker(keys, values):
    """Marker : type 'mark;<cles>' etat '<valeurs>' (delimiteur ',')."""
    return Trait('mark;' + string_array(keys), string_array(values))


def layer(images, level_names, up_command, up_key, layer_name='Etat',
          description='', start_level=1, follow_property=''):
    """Embellishment (« Couche ») version 2 : 33 champs, dans l'ordre exact
    de Embellishment.myGetType().

    follow_property : si non vide, la couche ne defile plus par commande mais
    suit la valeur d'une propriete (champ 23). VASSAL accepte ici une simple
    propriete ou une expression BeanShell entre accolades
    (Expression.createSimplePropertyExpression). La sequence etant delimitee
    par ';', une expression a base de ternaires ':' n'a pas besoin d'y etre
    echappee."""
    fields = [
        '',            # 1  activateCommand (couche toujours active)
        CTRL,          # 2  activateModifiers
        '',            # 3  activateKey
        up_command,    # 4  upCommand
        CTRL,          # 5  upModifiers
        '',            # 6  upKey
        '',            # 7  downCommand
        CTRL,          # 8  downModifiers
        '',            # 9  downKey
        '',            # 10 resetCommand
        '',            # 11 resetKey
        '1',           # 12 resetLevel
        False,         # 13 drawUnderneathWhenSelected
        0,             # 14 xOff
        0,             # 15 yOff
        string_array(images),       # 16 imageName[]
        string_array(level_names),  # 17 commonName[]
        True,          # 18 loopLevels
        layer_name,    # 19 name
        '',            # 20 rndKey
        '',            # 21 rndText
        bool(follow_property),  # 22 followProperty
        follow_property,        # 23 propertyName
        1,             # 24 firstLevelValue
        1,             # 25 version (encodage moderne)
        True,          # 26 alwaysActive
        '',            # 27 activateKeyStroke
        up_key,        # 28 increaseKeyStroke
        '',            # 29 decreaseKeyStroke
        description,   # 30 description
        '1.0',         # 31 scale
        '',            # 32 onlyPropertyName
        'true',        # 33 onlyPropertyState
    ]
    return Trait('emb2;' + seq(';', *fields), str(start_level))


def build_piece(traits):
    """Assemble la chaine d'un PieceSlot : '+/null/<TYPE>/<ETAT>'.

    traits : du plus externe au plus interne, BasicPiece en dernier.
    Chaque niveau reencode le niveau interieur, ce qui echappe ses tabulations.
    """
    type_string = traits[-1].type
    state_string = traits[-1].state
    for t in reversed(traits[:-1]):
        type_string = seq('\t', t.type, type_string)
        state_string = seq('\t', t.state, state_string)
    return '+/' + seq('/', 'null', type_string, state_string)


def dynamic_property(key, commands, value='0', numeric=True,
                     min_value=0, max_value=999999, wrap=False, description=''):
    """DynamicProperty : une valeur numerique portee par la piece.

    commands : liste de (libelle, keystroke, changer) ou changer vaut
      ('I', increment) pour ajouter, ('P', valeur) pour fixer,
      ('R', invite) pour demander la valeur au joueur.
    """
    constraints = seq(',', numeric, min_value, max_value, wrap)
    encoded = []
    for label, key_stroke, changer in commands:
        encoded.append(seq(':', label, key_stroke, seq(',', *changer)))
    return Trait(
        'PROP;' + seq(';', key, constraints, seq(',', *encoded), description),
        str(value),
    )


def labeler(text, font_size=26, fg='0,0,0', bg='',
            v_pos='c', h_pos='c', v_off=0, h_off=0,
            font_family='Dialog', font_style=1, description='',
            label_key='', menu_command='', property_name=''):
    """Labeler (« Etiquette texte »). Le texte est evalue comme un format :
    « $Montant$ » affiche donc la valeur de la propriete Montant.
    Passer label_key/menu_command pour une etiquette editable par le joueur
    (menu contextuel), sinon l'etiquette est en lecture seule."""
    fields = [
        label_key,     # 1  labelKey (commande d'edition, vide = lecture seule)
        menu_command,  # 2  menuCommand
        font_size,     # 3  taille
        bg,            # 4  fond
        fg,            # 5  texte
        v_pos,         # 6  position verticale
        v_off,         # 7  decalage vertical
        h_pos,         # 8  position horizontale
        h_off,         # 9  decalage horizontal
        'c',           # 10 justification verticale
        'c',           # 11 justification horizontale
        '$pieceName$', # 12 format du nom
        font_family,   # 13 police
        font_style,    # 14 style
        0,             # 15 rotation
        property_name, # 16 propriete exposee (vide = texte non lisible ailleurs)
        description,   # 17 description
        False,         # 18 toujours utiliser le format
    ]
    return Trait('label;' + seq(';', *fields), text)


def report_state(keys, report_format, description=''):
    """ReportState : envoie un message dans le journal quand l'une des
    touches de `keys` (liste de keystrokes) est actionnee sur la piece.
    Verifie par decodage reel : le trait traite d'abord les effets des
    traits interieurs (ex. DynamicProperty), donc `report_format` peut
    lire la valeur A JOUR (ex. « $PieceName$: $Value$ »)."""
    fields = [
        seq(',', *keys),  # 1 touches surveillees
        report_format,    # 2 format du message
        '',                # 3 touches de cycle descendant
        '',                # 4 formats de cycle descendant
        description,       # 5 description
        False,              # 6 ne pas supprimer si aucun changement
    ]
    return Trait('report;' + seq(';', *fields), '')


def hideable(hide_key, command='Hide/Reveal', bg='0,0,0', access='side:',
             transparency=0.5, description=''):
    """Hideable (« Piece masquee ») : une meme touche masque puis revele la
    piece. access='side:' restreint la visibilite au camp qui l'a masquee
    (VASSAL.configure.PieceAccessConfigurer). Etat: 'null' = visible de
    tous ; sinon le nom du camp qui la masque."""
    fields = [
        hide_key, command, bg, access, transparency, description, False,
    ]
    return Trait('hide;' + seq(';', *fields), 'null')


def obscurable(hide_key, mask_image, command='Mask', access='side:',
               mask_name='', description='', masked_by=None):
    """Obscurable (« Masquer ») : contrairement a Hideable, la piece reste
    VISIBLE des autres joueurs, mais ils en voient `mask_image` au lieu de son
    contenu reel. C'est ce que donne le style d'affichage 'G' (IMAGE) de
    Obscurable.mySetType() : le champ 4 vaut 'G' suivi du nom de l'image.

    access='side:' : seul le camp qui a masque la piece peut la reveler
    (VASSAL.counters.SideAccess.currentPlayerHasAccess/currentPlayerCanModify :
    verifie contre le code source).
    masked_by : si fourni (nom de camp), la piece nait DEJA masquee pour tous
    les autres camps - au lieu de naitre visible et d'attendre qu'un joueur
    appuie sur `hide_key`. Etat : 'null;' = non masquee ; sinon le camp qui
    la masque (Obscurable.mySetState/myGetState : verifie contre le code
    source)."""
    fields = [
        hide_key,               # 1  touche de masquage
        mask_image,             # 2  image vue quand un AUTRE camp l'a masquee
        command,                # 3  libelle du menu contextuel
        'G' + mask_image,       # 4  style d'affichage + image vue par les autres
        mask_name,              # 5  nom affiche quand masquee
        access,                 # 6  qui peut demasquer
        '',                     # 7  commande « jeter un oeil » (inutile en 'G')
        description,            # 8  description
        False,                  # 9  revelation auto au survol
        '',                     # 10 touche de distribution
        '',                     # 11 expression de distribution
    ]
    return Trait('obs;' + seq(';', *fields), seq(';', masked_by or 'null', ''))


def restricted(sides, restrict_by_player=False, restrict_movement=True, description=''):
    """Restricted (« Acces restreint ») : seul un joueur d'un des camps de
    `sides` peut agir sur la piece. Place comme trait le plus EXTERIEUR de
    tous ceux qu'il doit proteger : Restricted.getKeyCommands() renvoie
    KeyCommand.NONE pour tout autre camp, ce qui masque d'un coup les
    commandes de TOUS les traits interieurs (Obscurable, Labeler, etc.), et
    Restricted.keyEvent() renvoie null sans meme transmettre la touche aux
    traits interieurs (verifie contre VASSAL.counters.Restricted.java).
    restrict_movement=True empeche en plus tout autre camp de deplacer la
    piece a la souris."""
    fields = [string_array(sides), restrict_by_player, restrict_movement, description]
    return Trait('restrict;' + seq(';', *fields), '')


def send_to_location(command, key, x, y, map_name, board_name,
                     back_command='', back_key='', description=''):
    """SendToLocation : deplace la piece a des coordonnees fixes du plateau
    (destination 'L' = coordonnees directes, verifie contre le code source)."""
    fields = [
        command, key, map_name, board_name, str(x), str(y),
        back_command, back_key, '', '', 0, 0, description,
        'L', '', '', '', '',
    ]
    return Trait('sendto;' + seq(';', *fields), '')

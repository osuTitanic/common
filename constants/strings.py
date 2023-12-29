
ANCHOR_WEB_RESPONSE = '''
<pre>
        _-_
       |(_)|
        |||
        |||
        |||

        |||
        |||
  ^     |^|     ^
< ^ >   <a href="https://pbs.twimg.com/media/Dqnn54dVYAAVuki.jpg"><+></a>   < ^ >
 | |    |||    | |
  \ \__/ | \__/ /
    \,__.|.__,/
        (_)

titanic: <a href="https://github.com/osuTitanic/titanic">https://github.com/osuTitanic/titanic</a>
anchor: <a href="https://github.com/osuTitanic/anchor">https://github.com/osuTitanic/anchor</a>
stern: <a href="https://github.com/osuTitanic/stern">https://github.com/osuTitanic/stern</a>
deck: <a href="https://github.com/osuTitanic/deck">https://github.com/osuTitanic/deck</a>
</pre>
'''

ANCHOR_ASCII_ART = '''
        _-_
       |(_)|
        |||
        |||
        |||

        |||
        |||
  ^     |^|     ^
< ^ >   <+>   < ^ >
 | |    |||    | |
  \ \__/ | \__/ /
    \,__.|.__,/
        (_)
'''

MANIA_NOT_SUPPORTED = '\n'.join([
    'Your version of osu! does not support mania.',
    'Please upgrade to version b20121003 or higher!'
])

LOGGED_IN_FROM_ANOTHER_LOCATION = '\n'.join([
    'Another player has logged in to your account, from another location.',
    'Please change your password immediately, if this login was not authorized by you!'
])

UNSUPPORTED_VERSION = '\n'.join([
    'This version of osu! you are using is not compatible with this server.',
    'Please downgrade to one of our supported builds, or ask an admin for permission!'
])

UNSUPPORTED_HASH = '\n'.join([
    'This version of osu! you are using is not compatible with this server.',
    'Please download one of the clients on the website, or ask an admin for permission!'
])

MULTIACCOUNTING_DETECTED = '\n'.join([
    'Our systems have detected that you are multiaccounting.',
    'If you attempt to submit any scores, you will most likely be banned.',
    'If you believe this is a mistake, please contact an admin!'
])

MAINTENANCE_MODE = 'Bancho is currently in maintenance mode. Please check back later!'
MAINTENANCE_MODE_ADMIN = 'Bancho is currently in maintenance mode. Type !system maintenance off to disable it.'

# Taken from: https://m1.ppy.sh/release/filter.txt
BAD_WORDS = [
    'motherfucker',
    'ahole',
    'anus',
    'ash0le',
    'ash0les',
    'asholes',
    'assface',
    'assh0le',
    'assh0lez',
    'asshole',
    'assholes',
    'assholz',
    'asswipe',
    'azzhole',
    'bassterds',
    'bastard',
    'bastards',
    'bastardz',
    'basterds',
    'basterdz',
    'biatch',
    'bitch',
    'bitches',
    'blow job',
    'boffing',
    'butthole',
    'buttwipe',
    'c0ck',
    'c0cks',
    'c0k',
    'carpet muncher',
    'cawk',
    'cawks',
    'clit',
    'cnts',
    'cntz',
    'cock',
    'cockhead',
    'cock-head',
    'cocks',
    'cocksucker',
    'cock-sucker',
    'crap',
    'cunt',
    'cunts',
    'cuntz',
    'dick',
    'dild0',
    'dild0s',
    'dildo',
    'dildos',
    'dilld0',
    'dilld0s',
    'dominatricks',
    'dominatrics',
    'dominatrix',
    'dyke',
    'enema',
    'f u c k',
    'f u c k e r',
    'fag',
    'fag1t',
    'faget',
    'fagg1t',
    'faggit',
    'faggot',
    'fagit',
    'fags',
    'fagz',
    'faig',
    'faigs',
    'fart',
    'flipping the bird',
    'fuck',
    'fucker',
    'fuckin',
    'fucking',
    'fucks',
    'fudge packer',
    'fuk',
    'fukah',
    'fuken',
    'fuker',
    'fukin',
    'fukk',
    'fukkah',
    'fukken',
    'fukker',
    'fukkin',
    'g00k',
    'gay',
    'gayboy',
    'gaygirl',
    'gays',
    'gayz',
    'god-damned',
    'h00r',
    'h0ar',
    'h0re',
    'hells',
    'hoar',
    'hoor',
    'hoore',
    'jackoff',
    'japs',
    'jerk-off',
    'jisim',
    'jiss',
    'jizm',
    'jizz',
    'knob',
    'knobs',
    'knobz',
    'kunt',
    'kunts',
    'kuntz',
    'lesbian',
    'lezzian',
    'lipshits',
    'lipshitz',
    'masochist',
    'masokist',
    'massterbait',
    'masstrbait',
    'masstrbate',
    'masterbaiter',
    'masterbate',
    'masterbates',
    'motha fucker',
    'motha fuker',
    'motha fukkah',
    'motha fukker',
    'mother fucker',
    'mother fukah',
    'mother fuker',
    'mother fukkah',
    'mother fukker',
    'mother-fucker',
    'mutha fucker',
    'mutha fukah',
    'mutha fuker',
    'mutha fukkah',
    'mutha fukker',
    'n1gr',
    'nastt',
    'nigger',
    'nigur',
    'niiger',
    'niigr',
    'orafis',
    'orgasim',
    'orgasm',
    'orgasum',
    'oriface',
    'orifice',
    'orifiss',
    'packi',
    'packie',
    'packy',
    'paki',
    'pakie',
    'paky',
    'pecker',
    'peeenus',
    'peeenusss',
    'peenus',
    'peinus',
    'pen1s',
    'penas',
    'penis',
    'penis-breath',
    'penus',
    'penuus',
    'phuc',
    'phuck',
    'phuk',
    'phuker',
    'phukker',
    'polac',
    'polack',
    'poonani',
    'pr1c',
    'pr1ck',
    'pr1k',
    'pusse',
    'pussee',
    'pussy',
    'puuke',
    'puuker',
    'queer',
    'queers',
    'queerz',
    'qweers',
    'qweerz',
    'qweir',
    'recktum',
    'rectum',
    'retard',
    'sadist',
    'scank',
    'schlong',
    'screwing',
    'semen',
    'sex',
    'sexy',
    'sh!t',
    'sh1t',
    'sh1ter',
    'sh1ts',
    'sh1tter',
    'sh1tz',
    'shit',
    'shits',
    'shitter',
    'shitty',
    'shity',
    'shitz',
    'shyt',
    'shyte',
    'shytty',
    'shyty',
    'skanck',
    'skank',
    'skankee',
    'skankey',
    'skanks',
    'skanky',
    'slut',
    'sluts',
    'slutty',
    'slutz',
    'son-of-a-bitch',
    'tits',
    'turd',
    'va1jina',
    'vag1na',
    'vagiina',
    'vagina',
    'vaj1na',
    'vajina',
    'vullva',
    'vulva',
    'w0p',
    'wh00r',
    'wh0re',
    'whore',
    'xrated',
    'xxx',
    'nigga'
]

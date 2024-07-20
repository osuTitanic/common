
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

NOT_ACTIVATED = '\n'.join([
    'Your account is not yet activated. '
    'Please check your email for activation instructions!'
])

UNSUPPORTED_HASH = '\n'.join([
    'The version of osu! you are using is made for testers only.',
    'Please download a different version of osu! from the website!'
])

MULTIACCOUNTING_DETECTED = '\n'.join([
    'Our systems have detected that you are using multiple accounts on this server.',
    'Please note that multiaccounting is not allowed, and will result in a ban.',
    'If you believe this is a mistake, please contact an admin for further assistance!'
])

MAINTENANCE_MODE = 'Bancho is currently in maintenance mode. Please check back later!'
MAINTENANCE_MODE_ADMIN = 'Bancho is currently in maintenance mode. Type !system maintenance off to disable it.'

# Taken from: https://m1.ppy.sh/release/filter.txt
BAD_WORDS = [
    'motherfucker',
    'anus',
    'asshole',
    'bastard',
    'bitch',
    'bitches',
    'blow job',
    'cockhead',
    'cocksucker',
    'cunt',
    'cunts',
    'dick',
    'dildo',
    'fag1t',
    'faget',
    'fagg1t',
    'faggit',
    'faggot',
    'fagit',
    'fags',
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
    'nigger',
    'nigur',
    'niiger',
    'niigr',
    'penis',
    'pussy',
    'screwing',
    'sex',
    'sexy',
    'slut',
    'whore',
    'nigga'
]

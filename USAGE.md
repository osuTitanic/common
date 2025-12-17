# Overview

Here is a quick overview of how to use this module.

## Configuration

Most parts of `common` are configured through `common.config`.
The config object is a pydantic settings model, which loads from environment variables (and an optional `.env`).

```python
from common.config import Config

config = Config()

print(config.POSTGRES_HOST)
print(config.POSTGRES_DSN)
print(config.OSU_BASEURL)
```

If you just need a quick, shared config instance, you can also use `config_instance`:

```python
from common.config import config_instance as config

print(config.DOMAIN_NAME)
```

## Constants

The `common.constants` module will provide you with various useful enums & flags, like `Mods`, `GameMode` and much more.

Here is an example of `GameMode`, which inherits from `IntEnum`:

```python
from common.constants import GameMode

mode = GameMode.Osu
print(mode == 0)  # true
print(mode == 1)  # False
print(mode.name)  # "Osu"
print(mode.value) # 0
```

Here is an example of `Mods`, which inherits from `IntFlag`:

```python
from common.constants import Mods

mods = Mods(2 + 1)
print(mods)       # <Mods.NoFail|Easy: 3>
print(mods.short) # NFEZ
print(mods.value) # 3

mods = Mods.from_string('HDHR')
print(mods)                   # <Mods.Hidden|HardRock: 24>
print(mods & Mods.Hidden)     # <Mods.Hidden: 8>
print(mods & Mods.DoubleTime) # <Mods.NoMod: 0> (None)

mods = mods & ~Mods.HardRock
print(mods) # <Mods.Hidden: 8>

mods = mods | Mods.DoubleTime
print(mods) # <Mods.Hidden|DoubleTime: 72>
```

## Database & Repositories

Titanic provides a class for interacting with the database using sqlalchemy, which can be found in `common.database.postgres`.
All database table schemas are stored inside `common.database.objects`, and are represented through simple python classes.

Here is a simple example of how you would query a user:

```python
from common.config import Config
from common.database import Postgres, DBUser

# Setup the database class
config = Config()
database = Postgres(config)

# Open a session
with database.managed_session() as session:
    user = session.query(DBUser) \
        .filter(DBUser.id == 1) \
        .first()

    print(user.name) # "BanchoBot"
```

However there is an even simpler way of interacting with the database - Repositories.

You can find them in `common.database.repositories`, and can be used like this:

```python
from common.database.repositories import users

# Query without a session
user = users.fetch_by_id(1)
print(user.name) # "BanchoBot"

# Query with a session
with database.managed_session() as session:
    user = users.fetch_by_id(1, session=session)
    print(user.name) # "BanchoBot"
```

## Storage & External Resources

Titanic can store data either to your local filesystem, or to an external object storage server.
For this we have set up a helper class, which can be found under `common.storage`.

Here is an example of how to use it:

```python
from common.config import Config
from common.storage import Storage

config = Config()
storage = Storage(config)

# Fetch data
avatar = storage.get_avatar(1)
replay = storage.get_replay(3256)
osr_file = storage.get_full_replay(3256)

# Write data
storage.upload_avatar(1, b'<image_data>')
storage.upload_replay(4665, b'<replay_data>')
storage.upload_screenshot(123, b'<image_data>')

# Delete data
storage.remove_replay(3256)
storage.remove_beatmap_file(45775769)
storage.remove_osz(122634)

# Check if file exists
storage.file_exists(3256, 'replays')

# List a directory/bucket
storage.list('avatars')

# Beatmap downloads
osu = storage.get_beatmap(727)
osz_stream = storage.get_osz(122634)  # requests.Response-like iterable

# Local / s3 helpers
osz_bytes = storage.get_osz_internal(122634)
osz_size = storage.get_osz_size(122634)
```

## Function Caching

Function caching is used to cache the results of a function, as the name suggests.
Here is how to use it:

```python
from common.helpers import caching

# Add cache with timeout of 10 seconds
@caching.ttl_cache(ttl=10)
def your_function():
    ...

# Add cache that never expires
@caching.lru_cache()
def your_function():
    ...
```

## Redis

A better way to cache your stuff would be through redis.
Titanic uses the standard `redis` library for communications with the redis server.

Here is an example for it:

```python
from redis import Redis

redis = Redis(
    '<Host>',
    '<Port>'
)

redis.set('your:key', 1234)
redis.get('your:key') # 1234
redis.delete('your:key')
redis.exists('your:key') # false
```

There is a lot more stuff that redis offers, so I would highly recommend reading through their documentation.

### Leaderboards

Speaking of features that redis provides - Titanic uses redis sorted sets (ZSETs) to manage player leaderboards.
We provide a seperate python module for that, which can be found in `common.cache.leaderboards`.

```python
from common.cache import leaderboards

# Fetch ranks
leaderboards.global_rank(user_id=2, mode=0)
leaderboards.country_rank(user_id=2, mode=0, country='US')
leaderboards.score_rank(user_id=2, mode=0)
leaderboards.ppv1_rank(user_id=2, mode=0)

# Fetch "scores"
leaderboards.performance(user_id=2, mode=0)
leaderboards.score(user_id=2, mode=0)
leaderboards.total_score(user_id=2, mode=0)

# Fetch leaderboards
leaderboards.top_players(
    mode=0,
    offset=0,
    range=50,
    type='performance'
)

# Fetch leaderboards by country
leaderboards.top_players(
    mode=0,
    offset=0,
    range=50,
    type='performance',
    country='DE'
)

# Fetch country leaderboard
leaderboards.top_countries(mode=0)
```

### Player Statuses

The bancho status object is stored inside redis for all players, and can be accessed using the `common.cache.status` module.

```python
from common.cache import status

user_id = 2

status.exists(user_id) # Check if a player is connected to bancho
status.version(user_id) # Get the current version of the players client
status.get(user_id) # Returns bUserStats object
status.get_keys() # Get all status keys
status.client_hash(user_id) # Get the client hash of a player

# Functions that should only be used by bancho
status.delete(user_id)
status.update(user_id, ...)
```

### Events (pub/sub queue)

Redis provides a handy tool to communicate between different services, which are called "Channels".
Any service can "subscribe" to channels, to get updates for it.

As an example scenario, the "subscriber" will be bancho itself, who will always listen for any
incoming messages, and the sender will be the score server, who will push an announcement.

Here is the code for the subscriber:

```python
events = EventQueue(
    name='bancho:events',
    connection=redis
)

@events.register('announcement')
def announcement(message: str):
    print(f'Announcement: "{message}"')

# This will run in the background, to listen for messages.
def event_listener():
    """This will listen for redis pubsub events and call the appropriate functions."""
    events = events.listen()

    for func, args, kwargs in events:
        func(*args, **kwargs)
```

And here the sender:

```python
events = EventQueue(
    name='bancho:events',
    connection=redis
)

# Submit the event to bancho's queue
events.submit(
    'announcement',
    message="Hello, World!"
)
```

### Activity Counters

If you need a tiny redis-backed counter for "how many users are connected", you can use `common.cache.activity`.

```python
from common.cache import activity

activity.set_osu(123)
activity.set_irc(45)
activity.set_mp(6)

print(activity.get_all())  # {'osu': 123, 'irc': 45, 'mp': 6}
```

## Discord Logging (Officer)

Our Discord logging module "officer", is used to send various anomalies to our moderators.
The usage of it is very simple:

```python
from common import officer

example_exc = Exception()

officer.call("Something bad happened...")
officer.call("You can also send exceptions", exc_info=example_exc)
```

## Discord Events

Similar to officer, you can also send in events, which are meant to be public for everyone to see.
An example usecase for it would be a new forum post, or a new beatmap upload.

```python
from common import officer, webhooks

officer.event("BlueChin sucks.")
officer.event(embeds=[webhooks.Embed("Hi.")])
```

## Discord Webhooks (Raw)

If you want to post webhooks directly (without going through officer), use `common.webhooks`.

```python
from common.webhooks import Webhook, Embed

embed = Embed(
    title="was",
    description="holy shit"
)

Webhook(
    url="<Your Discord webhook URL>",
    content="whitecat just got unbanned",
    embeds=[embed]
).post()
```

## Emails

You are able to send emails through the `app.common.mail` module.
Make sure you have set up the correct configuration.

```python
from common import mail

mail.send(
    subject="Hello, your computer has virus.",
    message="My name is john smith, and you have been hacked.",
    email="target@example.com"
)

# There are also pre-defined email templates
mail.send_welcome_email(...)
mail.send_password_reset_email(...)
mail.send_password_changed_email(...)
mail.send_email_changed(...)
mail.send_reactivate_account_email(...)
mail.send_new_location_email(...)
```

## Geolocation

You can get the geolocation of an ip, using the `location` module inside `common.helpers.external`.
Here is an example of how to use it:

```python
from common.helpers.external import location

geolocation = location.fetch_geolocation("95.33.127.59")

# When using a private ip, the module will
# automatically look-up the public ip
geolocation = location.fetch_geolocation("127.0.0.1")

# Force geolocation look-up over database
geolocation = location.fetch_db("...")

# Force geolocation look-up over ip-api.com
geolocation = location.fetch_web("...")
```

## PP Calculations

`common.helpers.performance` provides calculation functions for both ppv1 and ppv2.

```python
from common.constants import GameMode, Mods
from common.helpers import performance
from common.database import scores

# Fetch a score for calculation
score = scores.fetch_by_id(142)

# Calculate ppv2
pp = performance.calculate_ppv2(score)

# Calculate ppv2 difficulty
diff = performance.calculate_difficulty(
    b"<beatmap_file>",
    GameMode.Osu,
    Mods.NoMod
)

# Calculate ppv1
pp = performance.calculate_ppv1(score)
```

## Binary Streams

This module provides two classes for dealing with binary streams: `StreamIn` & `StreamOut`.
Both of them are inside the `common.helpers.streams` module, and have primarily been used for bancho packets in the past.

```python
from common.helpers.streams import StreamIn, StreamOut

out = StreamOut(endian="<")
out.u32(123)
out.string("Hello, World!")
serialized = out.get()

stream = StreamIn(serialized, endian="<")
num = stream.u32() # 123
string = stream.string() # "Hello, World!"
```

## BBCode Rendering

Forum posts and other user content is formatted with BBCode.
The `common.bbcode` module can render that into HTML.

```python
from common.bbcode import render_html

html = render_html("[b]wysi[/b] [url=https://titanic.sh]Titanic![/url]")
print(html)
```

## Misc Helpers

This is a grab-bag of small utilities under `common.helpers`.

### IP Helpers

Resolve a real client IP when running behind proxies/CDNs:

```python
from common.helpers import ip

real_ip = ip.resolve_ip_address_fastapi(request)
is_local = ip.is_local_ip(real_ip)
```

### Permissions Helper

Check if a user has a certain permission:

```python
from common.helpers import permissions

if permissions.has_permission('admin.*', user_id=1):
    print('User is an admin')
```

### Chat Filters

Apply server-side chat filters (replacement + optional block timeout):

```python
from common.helpers.filter import ChatFilter

filters = ChatFilter()
filters.populate()

message, timeout = filters.apply("some message")
print(message, timeout)
```

## Profiling

If you have `pytracy` installed, you can enable profiling with tracy:

```python
from common import profiling

profiling.setup()
```

Please note that this requires the `0.11.1` release of [tracy](https://github.com/wolfpld/tracy/releases/tag/v0.11.1).

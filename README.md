
A folder used to share python code between bancho and the score server.

## How to use

```
app/
  common/
    ...
  session.py
```

The common folder expects a `session.py` file, located in the `app/` folder.
Inside that folder, there should be 4 objects:

- `redis` (`redis.Redis`)
- `database` (`app.common.database.Postgres`)
- `logger` (`logging.getLogger`)
- `requests` (`requests.Session`)

I will probably remove the requirement for the `app/` folder in the future, since that is pretty pointless.

## Content

- Postgres
    - Achievements
    - Activities
    - Beatmaps
    - Beatmapsets
    - Channels
    - Comments
    - Favourites
    - Histories
    - Logs
    - Messages
    - Plays
    - Ratings
    - Relationships
    - Scores
    - Screenshots
    - Stats
    - Users
- Helpers
    - Geolocation
    - Beatmap Resources
    - Performace
- Constants
    - Bancho
    - Country
    - Flags
    - Grade
    - Level
    - Modes
    - Mods
    - Multiplayer
    - Permissions
    - Regexes
    - Status
    - Strings
    - Web
- Bancho Objects
    - Achievements
    - Beatmaps
    - Chat
    - BanchoPacket
    - Multiplayer
    - Player
    - Spectator
- Redis
    - Leaderboards

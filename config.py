
from pydantic_settings import BaseSettings, SettingsConfigDict, NoDecode
from pydantic import Field, computed_field, field_validator
from typing_extensions import Annotated
from datetime import datetime

import os

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ## Database configuration
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "bancho"
    POSTGRES_DATABASE: str | None = None
    POSTGRES_PASSWORD: str

    POSTGRES_POOL_ENABLED: bool = True
    POSTGRES_POOL_SIZE: int = 10
    POSTGRES_POOL_SIZE_OVERFLOW: int = 30
    POSTGRES_POOL_PRE_PING: bool = True
    POSTGRES_POOL_RECYCLE: int = 900
    POSTGRES_POOL_TIMEOUT: int = 15

    ## Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_POOLSIZE: int = 10

    ## S3 Storage configuration (optional)
    S3_BASEURL: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_ACCESS_KEY: str | None = None

    # If disabled, the data gets stored locally
    # Buckets will be created automatically when enabled
    S3_ENABLED: bool = Field(default=False, validation_alias="ENABLE_S3")

    # Path to store application data locally, if S3 is disabled
    DATA_PATH: str = Field(default_factory=lambda: os.path.abspath(".data"))

    # This icon will be visible inside the menu (optional)
    MENUICON_IMAGE: str | None = None
    MENUICON_URL: str | None = None

    # A comma-separated list of background image urls that will be seen in the menu
    SEASONAL_BACKGROUNDS: Annotated[list[str], NoDecode] = []

    # Discord webhook url for logging (optional)
    OFFICER_WEBHOOK_URL: str | None = None

    # Event webhook url for updates to beatmaps, forums, etc. (optional)
    EVENT_WEBHOOK_URL: str | None = None

    # Image proxy baseurl for bbcode, using go-camo (optional)
    # https://github.com/cactus/go-camo
    IMAGE_PROXY_BASEURL: str | None = None

    ## Email configuration (optional)
    # Supported providers: "sendgrid", "mailgun", "smtp"
    EMAIL_PROVIDER: str | None = None
    EMAIL_SENDER: str | None = None

    # SMTP configuration
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None

    # Sendgrid configuration
    SENDGRID_API_KEY: str | None = None

    # Mailgun configuration
    MAILGUN_API_KEY: str | None = None
    MAILGUN_URL: str = "api.eu.mailgun.net"

    ## Score server configuration
    WEB_HOST: str = "localhost"
    WEB_PORT: int = 80
    WEB_WORKERS: int = 5

    # Amount of scores that will be sent for rankings
    SCORE_RESPONSE_LIMIT: int = 50

    # Disable/Enable score submission for relax & autopilot
    ALLOW_RELAX: bool = False

    # This will allow unauthenticated osu! direct usage for old clients
    ALLOW_UNAUTHENTICATED_DIRECT: bool = True

    # This will award pp and rscore for approved/loved maps
    APPROVED_MAP_REWARDS: bool = False

    # Enable or disable beatmap submission
    BEATMAP_SUBMISSION_ENABLED: bool = False

    # Used to freeze rank graph updates, useful for pp recalculations
    FROZEN_RANK_UPDATES: bool = False

    # Similar to the previous config, this will disable all ppv1 recalculation tasks
    FROZEN_PPV1_UPDATES: bool = False

    ## Bancho configuration
    BANCHO_TCP_PORTS: Annotated[list[int], NoDecode] = [13380, 13381, 13382, 13383]
    BANCHO_HTTP_PORT: int = 5000
    BANCHO_WS_PORT: int = 5001
    BANCHO_IRC_PORT: int = 6667
    BANCHO_IRC_PORT_SSL: int = 6697
    BANCHO_WORKERS: int = 16

    # Enable/disable irc-based connections
    IRC_ENABLED: bool = True
    OSU_IRC_ENABLED: bool = True

    # SSL configuration (optional)
    BANCHO_SSL_KEYFILE: str | None = None
    BANCHO_SSL_CERTFILE: str | None = None
    BANCHO_SSL_VERIFY_FILE: str | None = None

    # This will enable maintenance mode. Only admins can connect in this state.
    # You can also enable this using the !system maintenance command
    BANCHO_MAINTENANCE: bool = False

    # The server will skip multiaccounting checks if set to True
    ALLOW_MULTIACCOUNTING: bool = False

    # These channels will be automatically joined when logging in
    AUTOJOIN_CHANNELS: Annotated[list[str], NoDecode] = ["#osu", "#announce"]

    # Used for bancho_connect.php endpoint (optional)
    # Make sure this ip is not proxied in any way
    BANCHO_IP: str | None = Field(default=None, validation_alias="PUBLIC_BANCHO_IP")

    # This will verify the hash of the client, if set to False
    # You will need to edit the "releases" table to make it actually usable
    # Admins will automatically bypass this check by default
    DISABLE_CLIENT_VERIFICATION: bool = True

    # Will reject any login attempt with a client above the specified version (optional)
    BANCHO_CLIENT_CUTOFF: int | None = None

    # Maximum allowed slots in multiplayer matches
    MULTIPLAYER_MAX_SLOTS: int = 8

    ## Website configuration
    FRONTEND_HOST: str = "localhost"
    FRONTEND_PORT: int = 8080
    FRONTEND_WORKERS: int = 4

    # A secret for validating session tokens
    # Set this to something unique
    FRONTEND_SECRET_KEY: str | None = None

    # This is the expiry time for authentication tokens
    FRONTEND_TOKEN_EXPIRY: int = 3600
    FRONTEND_REFRESH_EXPIRY: int = 2592000

    # Enable this if you are using an ssl certificate
    ENABLE_SSL: bool = False

    # If you have ssl enabled, but still want to use http set this to true
    ALLOW_INSECURE_COOKIES: bool | None = None

    # reCAPTCHA key configuration
    RECAPTCHA_SECRET_KEY: str | None = None
    RECAPTCHA_SITE_KEY: str | None = None

    # IDs of users whom appear to have everyone added as a friend
    SUPER_FRIENDLY_USERS: Annotated[list[int], NoDecode] = Field(default_factory=list)

    # Cutoff timestamp for showing "since the beginning" join dates
    BEGINNING_ENDED_AT: datetime = datetime(2023, 12, 31, 6, 0, 0)

    # Wiki configuration
    WIKI_REPOSITORY_OWNER: str = "osuTitanic"
    WIKI_REPOSITORY_NAME: str = "wiki"
    WIKI_REPOSITORY_BRANCH: str = "main"
    WIKI_REPOSITORY_PATH: str = "wiki"
    WIKI_DEFAULT_LANGUAGE: str = "en"

    ## API configuration
    API_HOST: str = "localhost"
    API_PORT: int = 8000
    API_WORKERS: int = 4

    # Ratelimiting configuration
    API_RATELIMIT_ENABLED: bool = True
    API_RATELIMIT_WINDOW: int = 60
    API_RATELIMIT_REGULAR: int = 400
    API_RATELIMIT_AUTHENTICATED: int = 800

    # Ko-Fi token for donation callbacks
    KOFI_VERIFICATION_TOKEN: str | None = None
    
    # Bitview configuration (optional)
    BITVIEW_API_ENDPOINT: str | None = None
    BITVIEW_USERNAME: str | None = None
    BITVIEW_CLOUDFLARE_SOLVER: str | None = None

    ## Discord bot configuration (optional)
    ENABLE_DISCORD_BOT: bool = False
    DISCORD_BOT_PREFIX: str = "!"
    DISCORD_BOT_TOKEN: str | None = None
    DISCORD_STAFF_ROLE_ID: str | None = None
    DISCORD_BAT_ROLE_ID: str | None = None

    # Used for importing data from the official servers (optional)
    OSU_CLIENT_ID: str | None = None
    OSU_CLIENT_SECRET: str | None = None

    # Used for redirecting chat messages from discord to #osu (optional)
    CHAT_WEBHOOK_URL: str | None = None
    CHAT_CHANNEL_ID: int | None = None
    CHAT_WEBHOOK_CHANNELS: Annotated[list[str], NoDecode] = Field(default_factory=lambda: ["#osu"])

    # Debugging options
    DEBUG: bool = False
    RELOAD: bool = False

    # The base domain name of your server, used for generating links
    DOMAIN_NAME: str = "localhost"

    # Custom url overrides (optional)
    OSU_BASEURL_OVERRIDE: str | None = Field(default=None, validation_alias="OSU_BASEURL")
    API_BASEURL_OVERRIDE: str | None = Field(default=None, validation_alias="API_BASEURL")
    STATIC_BASEURL_OVERRIDE: str | None = Field(default=None, validation_alias="STATIC_BASEURL")
    EVENTS_WEBSOCKET_OVERRIDE: str | None = Field(default=None, validation_alias="EVENTS_WEBSOCKET")
    LOUNGE_BACKEND_OVERRIDE: str | None = Field(default=None, validation_alias="LOUNGE_BACKEND")

    # Custom image services that can bypass the proxy
    VALID_IMAGE_SERVICES_OVERRIDE: list[str] = Field(
        validation_alias="VALID_IMAGE_SERVICES",
        default=[
            "ibb.co",
            "i.ibb.co",
            "i.imgur.com",
            "media.tenor.com",
            "cdn.discordapp.com",
            "media.discordapp.net"
        ]
    )

    @computed_field
    @property
    def EMAIL_DOMAIN(self) -> str | None:
        if not self.EMAIL_SENDER or "@" not in self.EMAIL_SENDER:
            return None
        return self.EMAIL_SENDER.split("@", 1)[1]

    @computed_field
    @property
    def EMAILS_ENABLED(self) -> bool:
        return bool(self.EMAIL_PROVIDER and self.EMAIL_SENDER)

    @computed_field
    @property
    def BANCHO_SSL_ENABLED(self) -> bool:
        return bool(self.BANCHO_SSL_KEYFILE and self.BANCHO_SSL_CERTFILE)

    @computed_field
    @property
    def DEFAULT_OSU_BASEURL(self) -> str:
        scheme = "https" if self.ENABLE_SSL else "http"
        return f"{scheme}://osu.{self.DOMAIN_NAME}"

    @computed_field
    @property
    def DEFAULT_API_BASEURL(self) -> str:
        scheme = "https" if self.ENABLE_SSL else "http"
        return f"{scheme}://api.{self.DOMAIN_NAME}"

    @computed_field
    @property
    def DEFAULT_STATIC_BASEURL(self) -> str:
        scheme = "https" if self.ENABLE_SSL else "http"
        return f"{scheme}://s.{self.DOMAIN_NAME}"

    @computed_field
    @property
    def DEFAULT_EVENTS_WEBSOCKET(self) -> str:
        scheme = "wss" if self.ENABLE_SSL else "ws"
        return f"{scheme}://api.{self.DOMAIN_NAME}/events/ws"

    @computed_field
    @property
    def DEFAULT_LOUNGE_BACKEND(self) -> str:
        scheme = "https" if self.ENABLE_SSL else "http"
        return f"{scheme}://lounge.{self.DOMAIN_NAME}"

    @computed_field
    @property
    def VALID_IMAGE_SERVICES(self) -> tuple[str, ...]:
        custom_services = set(self.VALID_IMAGE_SERVICES_OVERRIDE)
        custom_services.add(f'i.{self.DOMAIN_NAME}')
        custom_services.add(f'osu.{self.DOMAIN_NAME}')
        return tuple(custom_services)

    @computed_field
    @property
    def POSTGRES_DSN(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE or self.POSTGRES_USER}"
        )

    @computed_field
    @property
    def OSU_BASEURL(self) -> str:
        return self.OSU_BASEURL_OVERRIDE or self.DEFAULT_OSU_BASEURL

    @computed_field
    @property
    def API_BASEURL(self) -> str:
        return self.API_BASEURL_OVERRIDE or self.DEFAULT_API_BASEURL

    @computed_field
    @property
    def STATIC_BASEURL(self) -> str:
        return self.STATIC_BASEURL_OVERRIDE or self.DEFAULT_STATIC_BASEURL
    
    @computed_field
    @property
    def EVENTS_WEBSOCKET(self) -> str:
        return self.EVENTS_WEBSOCKET_OVERRIDE or self.DEFAULT_EVENTS_WEBSOCKET
    
    @computed_field
    @property
    def LOUNGE_BACKEND(self) -> str:
        return self.LOUNGE_BACKEND_OVERRIDE or self.DEFAULT_LOUNGE_BACKEND

    @computed_field
    @property
    def SITEMAP_ENABLED(self) -> bool:
        return self.DOMAIN_NAME in ("titanic.sh", "localhost")
    
    @computed_field
    @property
    def BITVIEW_ENABLED(self) -> bool:
        return bool(self.BITVIEW_API_ENDPOINT and self.BITVIEW_USERNAME)

    @computed_field
    @property
    def CHRISTMAS_MODE(self) -> bool:
        now = datetime.now()
        return any((
            (now.month == 12 and now.day >= 15),
            (now.month == 1 and now.day <= 5),
        ))

    @field_validator("SEASONAL_BACKGROUNDS", "AUTOJOIN_CHANNELS", "CHAT_WEBHOOK_CHANNELS", mode="before")
    @classmethod
    def parse_string_list(cls, v):
        if not isinstance(v, str):
            # We assume the value is already a list
            return v

        # We have a comma-separated string, remove whitespace and split by comma
        return [item.strip() for item in v.split(",") if item.strip()]

    @field_validator("SUPER_FRIENDLY_USERS", "BANCHO_TCP_PORTS", mode="before")
    @classmethod
    def parse_int_list(cls, v):
        if isinstance(v, int):
            return [v]

        if isinstance(v, list):
            return v

        # We have a comma-separated string, remove whitespace and split by comma
        return [
            int(item.strip().removeprefix("[").removesuffix("]"))
            for item in v.split(",") if item.strip()
        ]
    
    @field_validator("SMTP_PORT", "BANCHO_CLIENT_CUTOFF", "CHAT_CHANNEL_ID", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v
    
    @field_validator("ALLOW_INSECURE_COOKIES", mode="before")
    @classmethod
    def set_allow_insecure_cookies(cls, v, info):
        if v is not None:
            return v

        # Default to the inverse of ENABLE_SSL
        enable_ssl = info.data.get("ENABLE_SSL", False)
        debug = info.data.get("DEBUG", False)
        return (not enable_ssl) or debug

config_instance = Config()

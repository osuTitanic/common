
from app.common.database.objects import DBChatFilter
from app.common.database import filters

from re import RegexFlag, Pattern, compile
from typing import List, Tuple, Dict
from functools import lru_cache

class ChatFilter:
    def __init__(self) -> None:
        self.patterns: Dict[str, Pattern] = {}
        self.filters: List[DBChatFilter] = []

    def __repr__(self) -> str:
        return f'<ChatFilter ({len(self.filters)} filters)>'

    def __len__(self) -> int:
        return len(self.filters)

    def populate(self) -> None:
        self.filters = filters.fetch_all()

        for filter in self.filters:
            self.patterns[filter.name] = compile(
                filter.pattern,
                flags=RegexFlag.IGNORECASE
            )

    @lru_cache(maxsize=128)
    def apply(self, message: str) -> Tuple[str, int | None]:
        for chat_filter in self.filters:
            replacement = chat_filter.replacement or ""
            filter = self.patterns[chat_filter.name]

            # Create a processor function to handle matches
            processor = lambda m: self.process_match(
                m.group(0),
                replacement
            )

            # Apply filter & check if content has changed
            filtered_message = filter.sub(processor, message)
            is_filtered = filtered_message != message

            # Update message with filtered content
            message = filtered_message

            if not is_filtered:
                continue

            if not chat_filter.block:
                continue

            return message, chat_filter.block_timeout_duration or 60

        return message, None

    def process_match(self, original: str, replacement: str) -> str:
        if not original or not replacement:
            return replacement

        # Try to preserve the case of the original text
        if original.islower():
            return replacement.lower()

        if original.isupper():
            return replacement.upper()

        if original.istitle():
            return replacement.title()

        return replacement

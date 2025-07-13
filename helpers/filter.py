
from app.common.database.objects import DBChatFilter
from app.common.database import filters
from app.common import officer

from re import RegexFlag, Pattern, compile
from typing import List, Tuple, Dict

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

    def apply(self, message: str) -> Tuple[str | None, int | None]:
        for chat_filter in self.filters:
            replacement = chat_filter.replacement or ""
            filter = self.patterns[chat_filter.name]

            # Apply filter & check if content has changed
            filtered_message = filter.sub(replacement, message)
            is_filtered = filtered_message != message

            # Update message with filtered content
            message = filtered_message

            if not is_filtered:
                continue

            if not chat_filter.block:
                continue

            return None, chat_filter.block_timeout_duration or 60

        return message, None

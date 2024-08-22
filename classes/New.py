import re
from datetime import date


class New:
    """Represents a new extracted from a website"""

    def __init__(
        self,
        title: str,
        publish_date: date,
        pic_filename: str,
        search_phrase_count: int,
        description: str | None = None,
    ):
        self._title = title
        self._publish_date = publish_date
        self._pic_filename = pic_filename
        self._search_phrase_count = search_phrase_count
        self._description = description

        money_pattern = re.compile(
            r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?"
            r"|\d+(?:,\d{3})*(?:\.\d{2})?\s+(dollars|USD)"
        )
        self._contains_money_amount = bool(
            money_pattern.search(f"{self._title}|{self._description or ''}")
        )

    @property
    def title(self):
        return self._title

    @property
    def publish_date(self):
        return self._publish_date

    @property
    def pic_filename(self):
        return self._pic_filename

    @property
    def search_phrase_count(self):
        return self._search_phrase_count

    @property
    def description(self):
        return self._description

    @property
    def contains_money_amount(self):
        return self._contains_money_amount

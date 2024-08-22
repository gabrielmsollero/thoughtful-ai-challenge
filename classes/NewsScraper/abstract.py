from abc import ABC, abstractmethod
from datetime import date
from RPA.core.webdriver import WebDriver
from typing import List

from classes.New import New


class NewsScraper(ABC):
    """Abstract base class to be used by site-specific scrapers in order to be
    usable by the task"""

    def __init__(self, driver: WebDriver, image_dir: str):
        self._driver = driver
        self._image_dir = image_dir

    def _get_limit_date(self, months: int):
        if months < 0:
            raise ValueError(
                f"parameter 'months' must be greater than 0. Received {months}"
            )

        months = max(months, 1)

        today = date.today()

        target_year = today.year
        target_month = today.month - (months - 1)

        while target_month < 1:
            target_month += 12
            target_year -= 1

        return date(target_year, target_month, 1)

    def _is_older_than_limit_date(self, tested_date: date, months: int):
        limit_date = self._get_limit_date(months)
        return tested_date < limit_date

    @abstractmethod
    def find(self, search_phrase: str, section: str, months: int) -> List[New]:
        pass

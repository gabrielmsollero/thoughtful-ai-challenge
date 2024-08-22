from abc import ABC, abstractmethod
from RPA.core.webdriver import WebDriver
from typing import List

from classes.New import New


class NewsScraper(ABC):
    """Abstract base class to be used by site-specific scrapers in order to be
    usable by the task"""

    # have a list of allowed sections from the website's visible ones and translate to routes
    # if user provides invalid section, raise error and tell the possible values

    def __init__(self, driver: WebDriver, image_dir: str):
        self._driver = driver
        self._image_dir = image_dir

    @abstractmethod
    def find(self, search_phrase: str, section: str, months: int) -> List[New]:
        pass

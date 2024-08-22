from typing import List
from datetime import date

from .abstract import NewsScraper as _NewsScraper
from classes.New import New


class NewsScraper(_NewsScraper):
    def find(self, search_phrase: str, section: str, months: int) -> List[New]:
        # define available sections and their corresponding url
        # assemble url from section and search_phrase
        # extract title
        # extract date
        # extract description
        # save picture to imgs directory
        # count search phrases in title and description
        # create New obj
        # append to returned list

        return [
            New("first new", date.today(), "imgs/first_new.png", 1),
            New(
                "second new",
                date.today(),
                "imgs/second_new.png",
                2,
                "second new description",
            ),
        ]

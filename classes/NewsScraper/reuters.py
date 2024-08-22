import logging
import os
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (
    text_to_be_present_in_element,
    presence_of_element_located,
)
from selenium.webdriver.support.wait import WebDriverWait
from typing import List
from uuid import uuid4

from .abstract import NewsScraper as _NewsScraper
from classes.New import New


class Locators:
    SEARCH_RESULT_TEXT = (By.CSS_SELECTOR, "h1#main-content")
    SEARCH_RESULT_ITEM = (By.CSS_SELECTOR, "li[class*='search-results__item']")
    RESULT_ITEM_TITLE = (By.CSS_SELECTOR, "header")
    RESULT_ITEM_DATE = (By.CSS_SELECTOR, "time")
    RESULT_ITEM_IMG = (By.CSS_SELECTOR, "img")
    NEXT_PAGE_BTN = (
        By.CSS_SELECTOR,
        "div[class*='search-results__pagination'] button:last-child",
    )


class NewsScraper(_NewsScraper):
    _logger = logging.getLogger(__name__)

    _sections = {
        "All": "all",
        "World": "world",
        "Business": "business",
        "Legal": "legal",
        "Markets": "markets",
        "Breakingviews": "breakingviews",
        "Technology": "technology",
        "Sustainability": "sustainability",
        "Science": "science",
        "Sports": "sports",
        "Lifestyle": "lifestyle",
    }

    def _assemble_url(self, search_phrase: str, section: str):
        return f"https://www.reuters.com/site-search/?query={'+'.join(search_phrase.split(' '))}&section={section}"

    def _wait_results_load(self):
        try:
            WebDriverWait(self._driver, 10).until(
                text_to_be_present_in_element(Locators.SEARCH_RESULT_TEXT, "result")
            )
        except (NoSuchElementException, TimeoutException):
            raise Exception("Could not find results section. Aborting scrape.")

    def find(self, search_phrase: str, section: str, months: int) -> List[New]:
        self._logger.info(
            f"starting search for '{search_phrase}' in section '{section}'"
        )

        if section not in self._sections.keys():
            raise ValueError(
                f"unknown section '{section}'. Accepted values are: {', '.join(self._sections.keys())}"
            )

        news: List[New] = []

        url = self._assemble_url(search_phrase, self._sections[section])
        self._driver.get(url)

        self._wait_results_load()

        done = False

        while not done:
            new_elements = self._driver.find_elements(*Locators.SEARCH_RESULT_ITEM)
            if len(new_elements) == 0:
                self._logger.info("could not find any news; stopping scrape")
                done = True
                break

            for new_element in new_elements:
                try:
                    WebDriverWait(new_element, 10).until(
                        presence_of_element_located(Locators.RESULT_ITEM_DATE)
                    )
                    date_element = new_element.find_element(*Locators.RESULT_ITEM_DATE)
                    date_text = date_element.get_attribute("innerText")
                    date = datetime.strptime(date_text, "%B %d, %Y").date()
                except (NoSuchElementException, TimeoutException):
                    self._logger.warning("could not find new date; discarding")
                    continue
                except ValueError:
                    self._logger.warning(
                        f"found date '{date_text}', but could not parse to date object; discarding"
                    )
                    continue

                if self._is_older_than_limit_date(date, months):
                    self._logger.info(
                        f"reached date before desired months: {date_text}; stopping scrape"
                    )
                    done = True
                    break

                try:
                    WebDriverWait(new_element, 10).until(
                        presence_of_element_located(Locators.RESULT_ITEM_TITLE)
                    )
                    title_element = new_element.find_element(
                        *Locators.RESULT_ITEM_TITLE
                    )
                    title = title_element.get_attribute("innerText")
                except (NoSuchElementException, TimeoutException):
                    self._logger.warning("could not find new title; discarding")
                    continue

                search_phrase_count = title.count(search_phrase)

                try:
                    WebDriverWait(new_element, 10).until(
                        presence_of_element_located(Locators.RESULT_ITEM_IMG)
                    )
                    img_element = new_element.find_element(*Locators.RESULT_ITEM_IMG)
                    img_filename = os.path.join(self._image_dir, f"{str(uuid4())}.png")
                    with open(img_filename, "wb+") as f:
                        f.write(img_element.screenshot_as_png)

                except (NoSuchElementException, TimeoutException):
                    self._logger.warning("could not find new image; discarding")
                    continue
                except Exception as e:
                    self._logger.warning(
                        f"found image but could not save: {e.__class__.__name__} - {str(e)}; discarding"
                    )

                self._logger.info(f"processed new: {title}")
                news.append(New(title, date, img_filename, search_phrase_count))

            try:
                WebDriverWait(self._driver, 10).until(
                    presence_of_element_located(Locators.NEXT_PAGE_BTN)
                )
                next_page_btn = self._driver.find_element(*Locators.NEXT_PAGE_BTN)
            except (NoSuchElementException, TimeoutException):
                self._logger.warning(
                    "could not find button for next page; finishing search"
                )
                done = True
                continue

            if next_page_btn.get_attribute("disabled"):
                done = True
                continue

            next_page_btn.click()
            self._wait_results_load()

        self._logger.info(f"search finished; found {len(news)} news")
        return news

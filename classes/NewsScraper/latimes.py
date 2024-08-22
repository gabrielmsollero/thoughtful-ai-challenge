import logging
import os
from datetime import date
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (
    text_to_be_present_in_element,
)
from selenium.webdriver.support.wait import WebDriverWait
from typing import List
from uuid import uuid4

from .abstract import NewsScraper as _NewsScraper
from classes.New import New


class Locators:
    SEARCH_RESULT_SECTION = (By.CSS_SELECTOR, "div.search-results-module-wrapper")
    SEARCH_RESULT_ITEM = (By.CSS_SELECTOR, "li div.promo-wrapper")
    RESULT_ITEM_TITLE = (
        By.CSS_SELECTOR,
        ".promo-content .promo-title-container .promo-title",
    )
    RESULT_ITEM_DESCRIPTION = (
        By.CSS_SELECTOR,
        ".promo-content .promo-description",
    )
    RESULT_ITEM_DATE = (By.CSS_SELECTOR, ".promo-content .promo-timestamp")
    RESULT_ITEM_IMG = (By.CSS_SELECTOR, ".promo-media img")
    NEXT_PAGE_ANCHOR = (
        By.CSS_SELECTOR,
        "div.search-results-module-next-page a",
    )


class NewsScraper(_NewsScraper):
    _logger = logging.getLogger(__name__)

    def _assemble_url(self, search_phrase: str):
        return (
            f"https://www.latimes.com/search?q={'+'.join(search_phrase.split(' '))}&s=1"
        )

    def _wait_results_load(self):
        try:

            WebDriverWait(self._driver, 10).until(
                text_to_be_present_in_element(Locators.SEARCH_RESULT_SECTION, "result")
            )
        except (NoSuchElementException, TimeoutException):
            raise Exception("Could not find results section. Aborting scrape.")

    def find(self, search_phrase: str, _: str, months: int) -> List[New]:
        self._logger.info(f"starting search for '{search_phrase}'")
        news: List[New] = []

        url = self._assemble_url(search_phrase)
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
                    date_element = new_element.find_element(*Locators.RESULT_ITEM_DATE)
                    date_text = date_element.get_attribute("innerText")
                    date_timestamp = date_element.get_attribute("data-timestamp")
                    date_obj = date.fromtimestamp(int(date_timestamp) / 1000)
                except NoSuchElementException:
                    self._logger.warning("could not find new date; discarding")
                    continue
                except (TypeError, ValueError):
                    self._logger.warning(
                        f"found date '{date_text}', but could not parse to date object; discarding"
                    )
                    continue

                if self._is_older_than_limit_date(date_obj, months):
                    self._logger.info(
                        f"reached date before desired months: {date_text}; stopping scrape"
                    )
                    done = True
                    break

                try:
                    title_element = new_element.find_element(
                        *Locators.RESULT_ITEM_TITLE
                    )
                    title = title_element.get_attribute("innerText")
                except NoSuchElementException:
                    self._logger.warning("could not find new title; discarding")
                    continue

                try:
                    description_element = new_element.find_element(
                        *Locators.RESULT_ITEM_DESCRIPTION
                    )
                    description = description_element.get_attribute("innerText")
                except NoSuchElementException:
                    self._logger.warning(
                        "could not find new description; parsing anyways"
                    )
                    description = None

                search_phrase_count = f"{title}.{description or ''}".count(
                    search_phrase
                )

                has_image = True
                try:
                    img_element = new_element.find_element(*Locators.RESULT_ITEM_IMG)
                except NoSuchElementException:
                    self._logger.warning("could not find new image; parsing anyways")
                    has_image = False

                img_filename = ""
                if has_image:
                    try:
                        img_filename = os.path.join(
                            self._image_dir, f"{str(uuid4())}.png"
                        )
                        with open(img_filename, "wb+") as f:
                            f.write(img_element.screenshot_as_png)
                    except Exception as e:
                        self._logger.warning(
                            f"found image but could not save: {e.__class__.__name__} - {str(e)}; discarding"
                        )

                self._logger.info(f"processed new: {title}")
                news.append(
                    New(title, date_obj, img_filename, search_phrase_count, description)
                )

            try:
                next_page_anchor = self._driver.find_element(*Locators.NEXT_PAGE_ANCHOR)
            except NoSuchElementException:
                done = True

            if done:
                break

            self._driver.get(next_page_anchor.get_attribute("href"))
            self._wait_results_load()

        self._logger.info(f"search finished; found {len(news)} news")
        return news

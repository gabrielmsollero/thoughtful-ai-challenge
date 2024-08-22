import logging
from robocorp.tasks import task
from selenium import webdriver

from classes.NewsScraper.reuters import NewsScraper
from classes.NewsSpreadsheet import NewsSpreadsheet

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@task
def fetch_news_and_save_to_excel_task():
    # using CustomSelenium approach. RPA.core.webdriver.cache, used in the
    # given example, is deprecated so we're using selenium.webdriver instead
    # see https://stackoverflow.com/questions/78856991/importerror-cannot-import-name-cache-from-rpa-core-webdriver

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-web-security")
    options.add_argument("--start-maximized")
    options.add_argument("--remote-debugging-port=9222")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=options)
    scraper = NewsScraper(driver, "./output")

    news = scraper.find("test", "politics", 1)
    logging.info(f"fetched {len(news)} news; adding to spreadsheet")

    spreadsheet = NewsSpreadsheet()
    for n in news:
        spreadsheet.add_new(n)

    filename = "output/news.xlsx"
    logging.info(f'all news added to spreadsheet; saving to file "{filename}"')
    try:
        spreadsheet.save_to(filename)
        logging.info(f"spreadsheet saved successfully to '{filename}'")
    except Exception as e:
        logging.error(
            f"could not save spreadsheet to '{filename}'; {e.__class__.__name__} - {str(e)}"
        )
        raise Exception("could not write news spreadsheet to file")

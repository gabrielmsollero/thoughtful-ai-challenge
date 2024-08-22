from datetime import date
import logging
from RPA.Robocorp.WorkItems import WorkItems
from robocorp.tasks import task

from classes.New import New
from classes.NewsSpreadsheet import NewsSpreadsheet

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@task
def fetch_news_and_save_to_excel_task():
    news = [
        New("first new", date.today(), "imgs/first_new.png", 1),
        New(
            "second new",
            date.today(),
            "imgs/second_new.png",
            2,
            "second new description",
        ),
    ]

    logging.info(f"fetched {len(news)} news; adding to spreadsheet")

    news_spreadsheet = NewsSpreadsheet()

    for n in news:
        news_spreadsheet.add_new(n)

    filename = "output/news.xlsx"

    logging.info(f'all news added to spreadsheet; saving to file "{filename}"')

    try:
        news_spreadsheet.save_to(filename)
        logging.info(f"spreadsheet saved successfully to '{filename}'")
    except Exception as e:
        logging.error(
            f"could not save spreadsheet to '{filename}'; {e.__class__.__name__} - {str(e)}"
        )

        raise AssertionError("could not write news spreadsheet to file")

from .sources import PUBLIC_FEEDS
from .press import Press
from datetime import date, timedelta


def daterange(start_date, end_date, dayIncrement=1):
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=dayIncrement)

def backfillEditions(articles, start_date, end_date, editionDays=7):
    for d in daterange(start_date, end_date, editionDays):
        press = Press(d, PUBLIC_FEEDS)
        edition = press.constructEdition(articles, lookbackDays=editionDays)
        edition.writeFile()

# IPython helpers:
#
# %load_ext autoreload
# %autoreload 2
# from datetime import date, timedelta
# from gazette import Press
# from gazette.sources import PUBLIC_FEEDS

if __name__ == "__main__":
    press = Press(date.today(), PUBLIC_FEEDS)
    articles = press.fetchArticles()
    edition = press.constructEdition(articles, lookbackDays=7)

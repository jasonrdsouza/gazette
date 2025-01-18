from .sources import PUBLIC_FEEDS
from .press import Press
from datetime import date, timedelta


def daterange(start_date, end_date, dayIncrement=1):
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=dayIncrement)


# IPython helpers:
#
# %load_ext autoreload
# %autoreload 2
# from datetime import date
# from gazette import Press
# from gazette.config import FEEDS

if __name__ == "__main__":
    press = Press(date.today(), FEEDS)
    articles = press.fetchArticles()
    edition = press.constructEdition(articles, lookbackDays=3)

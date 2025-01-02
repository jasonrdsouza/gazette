import dataclasses
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List
import json
from pathlib import Path
import feedparser


@dataclass
class Article:
    title: str
    source: str
    publishedAt: date
    link: str
    summary: str
    content: List[str]

    def __repr__(self):
        return f"Article(title={self.title}, source={self.source}, publishedAt={self.publishedAt}, link={self.link}, summaryWords={self.summaryWordLength()}, contentWords={self.contentWordLength()})"

    def stringToWords(self, string) -> int:
        return string.split()

    def summaryWordLength(self):
        return len(self.stringToWords(self.summary))

    def contentWordLength(self):
        return sum(len(self.stringToWords(c)) for c in self.content)

    # def __post_init__(self):
    #     summaryWords = self.summary.split()
    #     if len(summaryWords) > SUMMARY_WORD_LIMIT:
    #         self.summary = " ".join(summaryWords[:SUMMARY_WORD_LIMIT])


@dataclass
class Edition:
    publishDate: date
    lookbackDays: int
    articles: List[Article]

    def __repr__(self):
        return f"Edition(publishedDate={self.publishDate}, lookbackDays={self.lookbackDays}, numArticles={len(self.articles)})"

    def headlines(self):
        return [(a.source, a.publishedAt, a.title) for a in self.articles]

    def toJson(self):
        return json.dumps(self, cls=EditionEncoder)

    def writeFile(self, path="editions"):
        p = Path(path)
        fullpath = p.joinpath(f"{self.publishDate.strftime("%Y%m%d")}.json")
        with fullpath.open(mode="w") as f:
            json.dump(self, f, cls=EditionEncoder)


class EditionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        elif dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)

        return super().default(obj)


class Press:
    def __init__(self, editionDate: date, feeds):
        self.editionDate = editionDate
        self.feeds = feeds

    # pulls content from rss feeds
    def fetchArticles(self) -> List[Article]:
        articles: List[Article] = []
        for name, url in self.feeds.items():
            fetched = feedparser.parse(url)
            for entry in fetched.entries:
                if "published" not in entry:
                    print(f"No published field for feed {name}, entry {entry.get('title', 'Untitled')}")
                else:
                    articles.append(
                        Article(
                            title=entry.get("title", "Untitled"),
                            source=name,
                            publishedAt=date(
                                entry.published_parsed.tm_year,
                                entry.published_parsed.tm_mon,
                                entry.published_parsed.tm_mday,
                            ),
                            link=entry.link,
                            summary=entry.get("summary", ""),
                            content=[c.value for c in entry.get("content", [])],
                        )
                    )

        return articles

    # For now, the only determinant of whether an article should be published is
    # how long ago it was written (with a sliding window to avoid missing articles)
    # which were published on the boundary of when my script runs.
    #
    # In the future, I may include more filtering criteria based on topics, etc.
    def shouldPublish(self, lookbackDays: int, article: Article) -> bool:
        return article.publishedAt < self.editionDate and (self.editionDate - article.publishedAt) < timedelta(
            days=lookbackDays
        )

    # constructs a JSON "edition" payload which the frontend gazette
    # can parse/ display. Output file should include the date in the filename
    def constructEdition(self, articles: List[Article], lookbackDays=3) -> Edition:
        articlesToPublish = [a for a in articles if self.shouldPublish(lookbackDays, a)]
        return Edition(self.editionDate, lookbackDays, list(articlesToPublish))

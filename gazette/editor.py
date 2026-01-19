import argparse
import feedparser
from collections import defaultdict
from gazette.press import parse_feed
from gazette.sources import add_source


def main():
    parser = argparse.ArgumentParser(description="Analyze an RSS feed.")
    parser.add_argument("url", help="The URL of the RSS feed to analyze")
    parser.add_argument(
        "--add-source",
        action="store_true",
        help="Add the provided RSS feed to the sources json file",
    )
    parser.add_argument(
        "--name",
        help="Manually specify the source name when adding a new source",
    )
    args = parser.parse_args()

    url = args.url

    if args.add_source:
        title = args.name
        if not title:
            print(f"Fetching feed metadata for: {url}")
            feed_data = feedparser.parse(url)

            # Try to find author
            if hasattr(feed_data, "feed") and hasattr(feed_data.feed, "author"):
                title = feed_data.feed.author
                print(f"Found author: {title}")

            # Fallback to title
            if (
                not title
                and hasattr(feed_data, "feed")
                and hasattr(feed_data.feed, "title")
            ):
                title = feed_data.feed.title
                print(f"Found title: {title}")

        if title:
            if add_source(title, url):
                print(f"Successfully added '{title}' to sources.")
            else:
                print(f"Source with URL '{url}' already exists.")
        else:
            print("Could not determine feed title. Cannot add source.")
        print("")

    print(f"Analyzing feed: {url}\n")

    articles, skipped = parse_feed("Editor Source", url)

    if not articles and not skipped:
        print("No entries found in feed.")
        return

    # Stats
    total_articles = len(articles)

    # Sort by date descending
    articles.sort(key=lambda a: a.publishedAt, reverse=True)

    if articles:
        # Filter out articles with extremely old dates (likely parsing errors or default values)
        # For this analysis, we'll consider anything before 1990 as invalid for frequency calculation
        valid_articles = [a for a in articles if a.publishedAt.year >= 1990]

        if not valid_articles:
            print("No articles found with valid dates (>= 1990).")
        else:
            newest = valid_articles[0].publishedAt
            oldest = valid_articles[-1].publishedAt
            days_span = (newest - oldest).days

            # Avoid division by zero and handle short spans
            if days_span == 0:
                weeks = 1 / 7  # Treat as 1 day
            else:
                weeks = days_span / 7

            avg_per_week = len(valid_articles) / weeks

            print(f"Total Articles: {total_articles}")
            print(f"Date Range: {oldest} to {newest} ({days_span} days)")
            print(f"Frequency: {avg_per_week:.2f} entries / week")
            print("")

            print("Recent Posts:")
            for i, article in enumerate(valid_articles[:5]):
                print(f"  {article.publishedAt} - {article.title}")
                print(f"    {article.link}")
            print("")

            print("Historical Distribution:")
            # Group by YYYY-MM
            history = defaultdict(int)
            for a in (
                articles
            ):  # Still show distribution for all, even invalid ones, so user sees them
                key = a.publishedAt.strftime("%Y-%m")
                history[key] += 1

            # Sort keys
            sorted_keys = sorted(history.keys(), reverse=True)
            for key in sorted_keys:
                print(f"  {key}: {history[key]}")
            print("")
    else:
        print(
            "No valid articles found (all were skipped or feed is empty of valid articles)."
        )
        print("")

    if skipped:
        print("Skipped Entries (Issues):")
        print(f"Total Skipped: {len(skipped)}")
        for entry in skipped:
            title = entry.get("title", "Untitled")
            print(f"  - {title} (Missing published/updated date)")
    else:
        print("No parsing issues encountered.")


if __name__ == "__main__":
    main()

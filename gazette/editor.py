import argparse
import ast
import subprocess
from collections import defaultdict
from pathlib import Path

from gazette.press import parse_feed


def add_source_to_file(name: str, url: str):
    sources_path = Path("gazette/sources.py")
    if not sources_path.exists():
        print(f"Error: {sources_path} not found.")
        return

    content = sources_path.read_text()

    # Simple parsing to find the dictionary
    # We assume the file structure is simple as seen previously: a single PUBLIC_FEEDS dict

    try:
        tree = ast.parse(content)
    except SyntaxError:
        print("Error: Could not parse gazette/sources.py")
        return

    # Find the assignment to PUBLIC_FEEDS
    feeds_dict = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PUBLIC_FEEDS":
                    if isinstance(node.value, ast.Dict):
                        feeds_dict = node.value
                        break
            if feeds_dict:
                break

    if not feeds_dict:
        print("Error: Could not find PUBLIC_FEEDS dictionary in gazette/sources.py")
        return

    # Extract current feeds
    current_feeds = {}
    for k, v in zip(feeds_dict.keys, feeds_dict.values):
        if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
             current_feeds[k.value] = v.value

    # Add new feed
    if name in current_feeds:
        print(f"Warning: Source '{name}' already exists. Updating URL.")

    current_feeds[name] = url

    # Sort keys
    sorted_keys = sorted(current_feeds.keys(), key=lambda s: s.lower())

    # Reconstruct the file content
    # We will rewrite the whole file for simplicity, assuming it just contains the dict
    # If the file has imports or other code, we should be careful.
    # Looking at the previous `read_file` of sources.py, it seemed to only contain the dict.
    # Let's check imports.

    new_content = "PUBLIC_FEEDS = {\n"
    for k in sorted_keys:
        new_content += f'    "{k}": "{current_feeds[k]}",\n'
    new_content += "}\n"

    sources_path.write_text(new_content)
    print(f"Added '{name}' to gazette/sources.py")

    # Run formatter
    try:
        subprocess.run(["uv", "run", "black", str(sources_path)], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print("Warning: Failed to run black formatter on gazette/sources.py")
        # Fallback to check if black is installed or just ignore if it fails (user might not have dev deps)


def main():
    parser = argparse.ArgumentParser(description="Analyze an RSS feed.")
    parser.add_argument("url", help="The URL of the RSS feed to analyze")
    parser.add_argument(
        "--add-source",
        metavar="NAME",
        help="Add the feed to sources.py with the given name",
    )
    args = parser.parse_args()

    url = args.url
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
        newest = articles[0].publishedAt
        oldest = articles[-1].publishedAt
        days_span = (newest - oldest).days

        # Avoid division by zero and handle short spans
        if days_span == 0:
            weeks = 1 / 7  # Treat as 1 day
        else:
            weeks = days_span / 7

        avg_per_week = total_articles / weeks

        print(f"Total Articles: {total_articles}")
        print(f"Date Range: {oldest} to {newest} ({days_span} days)")
        print(f"Frequency: {avg_per_week:.2f} entries / week")
        print("")

        print("Historical Distribution:")
        # Group by YYYY-MM
        history = defaultdict(int)
        for a in articles:
            key = a.publishedAt.strftime("%Y-%m")
            history[key] += 1

        # Sort keys
        sorted_keys = sorted(history.keys(), reverse=True)
        for key in sorted_keys:
            print(f"  {key}: {history[key]}")
        print("")
    else:
        print("No valid articles found (all were skipped or feed is empty of valid articles).")
        print("")

    if skipped:
        print("Skipped Entries (Issues):")
        print(f"Total Skipped: {len(skipped)}")
        for entry in skipped:
            title = entry.get("title", "Untitled")
            print(f"  - {title} (Missing published/updated date)")
    else:
        print("No parsing issues encountered.")

    # Add source if requested
    if args.add_source:
        print("")
        add_source_to_file(args.add_source, url)


if __name__ == "__main__":
    main()

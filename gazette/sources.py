import json
import pathlib

# Get the directory where this file (sources.py) is located
CURRENT_DIR = pathlib.Path(__file__).parent

# Path to the sources.json file
SOURCES_FILE = CURRENT_DIR / "sources.json"


def load_sources():
    with open(SOURCES_FILE, "r") as f:
        data = json.load(f)

    # Convert the list of dicts [{"name": "...", "url": "..."}] back to the expected dict format {name: url}
    # used by the rest of the application
    feeds = {}
    for source in data:
        feeds[source["name"]] = source["url"]
    return feeds


def add_source(name: str, url: str) -> bool:
    """
    Adds a new source to sources.json.
    Returns True if added, False if it already exists.
    """
    with open(SOURCES_FILE, "r") as f:
        data = json.load(f)

    # Check if URL already exists
    for source in data:
        if source["url"] == url:
            return False

    # Add new source
    data.append({"name": name, "url": url})

    # Sort by name for tidiness
    data.sort(key=lambda x: x["name"].lower())

    with open(SOURCES_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return True


PUBLIC_FEEDS = load_sources()

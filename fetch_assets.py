import os
import json
import logging
from screenwrite.fetchers.youtube_client import YouTubeClient
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AssetOrchestrator")

# Constants
OUTPUT_DIR = Path("webapp/backend/uploads/The Art of the Walkthrough")
INDEX_FILE = OUTPUT_DIR / "metadata_index.json"

# Visual Plan
PLAN = [
    {"segment": "Intro", "query": "1983 video game crash gameplay", "duration": 30},
    {"segment": "Nintendo Hotline", "query": "90s Nintendo Power hotline commercial", "duration": 20},
    {"segment": "Internet transition", "query": "90s dial-up internet animation", "duration": 15},
    {"segment": "IGN/Modern Guides", "query": "modern gaming walkthrough website ad", "duration": 30},
    {"segment": "YouTube Walkthroughs", "query": "game walkthrough video guide", "duration": 30},
    {"segment": "Wikis", "query": "Fextralife wiki browsing", "duration": 30},
]

def run_fetch():
    client = YouTubeClient(output_dir=str(OUTPUT_DIR))
    index = []

    for item in PLAN:
        logger.info(f"Fetching: {item['segment']}")
        path = client.fetch(item['query'], item['duration'])
        
        entry = {
            "segment": item['segment'],
            "original_query": item['query'],
            "file_path": str(path) if path else None,
            "needs_editing": True,
            "edit_notes": "Needs pan/zoom or text overlay effects." if item['segment'] in ["Intro", "Nintendo Hotline"] else ""
        }
        index.append(entry)

    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=4)
    
    logger.info(f"Process complete. Index saved to {INDEX_FILE}")

if __name__ == "__main__":
    run_fetch()

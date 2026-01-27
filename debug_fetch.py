import os
import sys
import json
import logging
import time

# Setup logging to stdout
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator

SESSION_ID = "1d227071-a092-4e77-ad19-a07c56d0bb09"
SESSION_DIR = f"webapp/backend/sessions/{SESSION_ID}"
STATE_FILE = f"{SESSION_DIR}/state.json"
ASSETS_DIR = f"{SESSION_DIR}/assets"

print(f"Loading state from {STATE_FILE}...")

with open(STATE_FILE, 'r') as f:
    state = json.load(f)

config = state.get('config', {})
beats = state.get('beats', [])

print(f"Config: {config}")
print(f"Found {len(beats)} beats")

# Ensure assets dir exists
os.makedirs(ASSETS_DIR, exist_ok=True)

print("Initializing Orchestrator...")
orchestrator = AssetOrchestrator(
    pexels_api_key=config.get('pexels_api_key'),
    output_dir=ASSETS_DIR,
    youtube_enabled=config.get('youtube_enabled', True),
    pexels_enabled=config.get('pexels_enabled', True)
)

print(f"Available fetchers: {[f.name for f in orchestrator.fetchers]}")

# Prepare queries (limit to 3 for test)
queries = []
for beat in beats[:3]:
    yt_phrase = beat.get('youtube_phrase', '')
    stock_keyword = beat.get('stock_keyword', '')
    
    if not yt_phrase and not stock_keyword:
        print(f"Skipping beat {beat['id']} (no keywords)")
        continue
        
    queries.append({
        'id': beat['id'],
        'youtube_query': yt_phrase,
        'stock_query': stock_keyword,
        'duration': beat['duration']
    })

print(f"Testing with {len(queries)} queries...")

results = orchestrator.fetch_assets_batch(queries, max_workers=1)

print("\nResults:")
for qid, path in results.items():
    print(f"{qid}: {path}")

import os
import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator

SESSION_ID = "1d227071-a092-4e77-ad19-a07c56d0bb09"
SESSION_DIR = f"webapp/backend/sessions/{SESSION_ID}"
ASSETS_DIR = f"{SESSION_DIR}/assets"

# Config from state
CONFIG = {
    'youtube_enabled': True,
    'pexels_enabled': True,
    'pexels_api_key': '',
    'output_dir': ASSETS_DIR
}

# Queries that failed according to state.json (value is null)
# We'll retry a few of these to debug why they fail
FAILED_QUERIES = [
    {
        'id': 'beat_002',
        'youtube_query': 'path through forest',
        'stock_query': 'writing',
        'duration': 10.0
    },
    {
        'id': 'beat_003',
        'youtube_query': 'baby hand holding',
        'stock_query': 'writing',
        'duration': 7.2
    },
    {
        'id': 'beat_004',
        'youtube_query': 'bad guide',
        'stock_query': 'writing',
        'duration': 5.6
    }
]

print("Initializing Orchestrator...")
orchestrator = AssetOrchestrator(
    pexels_api_key=CONFIG.get('pexels_api_key'),
    output_dir=ASSETS_DIR,
    youtube_enabled=CONFIG.get('youtube_enabled'),
    pexels_enabled=CONFIG.get('pexels_enabled')
)

print(f"Testing {len(FAILED_QUERIES)} failed queries...")

# Try batch fetch again
results = orchestrator.fetch_assets_batch(FAILED_QUERIES, max_workers=1)

print("\nResults:")
for qid, path in results.items():
    status = "SUCCESS" if path else "FAILED"
    print(f"{qid}: {status} - {path}")

import os
import json
import datetime

sessions_dir = 'webapp/backend/sessions'
sessions = []

if os.path.exists(sessions_dir):
    for session_id in os.listdir(sessions_dir):
        path = os.path.join(sessions_dir, session_id)
        state_path = os.path.join(path, 'state.json')
        
        if os.path.isdir(path) and os.path.exists(state_path):
            try:
                with open(state_path, 'r') as f:
                    state = json.load(f)
                    
                updated = state.get('updatedAt') or state.get('exportedAt')
                if not updated:
                    # Fallback to file mtime
                    mtime = os.path.getmtime(state_path)
                    updated = datetime.datetime.fromtimestamp(mtime).isoformat()
                
                beats = state.get('beats', [])
                beat_count = len(beats)
                first_beat = beats[0].get('text', '')[:50] + "..." if beats else "No beats"
                
                sessions.append({
                    'id': session_id,
                    'updated': updated,
                    'beats': beat_count,
                    'preview': first_beat
                })
            except Exception as e:
                continue

# Sort by updated desc
sessions.sort(key=lambda x: x['updated'], reverse=True)

print(f"{'SESSION ID':<38} | {'UPDATED':<20} | {'BEATS':<5} | {'PREVIEW'}")
print("-" * 100)
for s in sessions:
    print(f"{s['id']:<38} | {s['updated'][:19]:<20} | {s['beats']:<5} | {s['preview']}")

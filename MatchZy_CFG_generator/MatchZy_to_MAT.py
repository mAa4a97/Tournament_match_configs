import json
import os
from glob import glob

# Folder containing the individual team JSON files
INPUT_FOLDER = "teams"

# Output file
OUTPUT_FILE = "MAT_teams.json"

teams = []

for file_path in glob(os.path.join(INPUT_FOLDER, "*.json")):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    team = {
        "name": data["name"],
        "players": [
            {
                "steamId": steam_id,
                "name": player_name
            }
            for steam_id, player_name in data["players"].items()
        ]
    }

    teams.append(team)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(teams, f, indent=2, ensure_ascii=False)

print(f"Converted {len(teams)} teams into {OUTPUT_FILE}")
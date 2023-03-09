#!/usr/bin/env python3

import json
import os
import csv
from services import riot_api
from parsers.match_parser import parse_match
from parsers.timeline_parser import parse_frame, parse_sequence
import time
from datetime import datetime

TEAM_ID_BLUE = 100
TEAM_ID_RED = 200

# Information extracted from the Match-V5 Endpoint
MATCH_DATA_HEADERS = [
    'tier',
    'division',
    'match_id',
    'label'
]

FRAME_DATA_HEADERS = [
    'blue_top_xp',
    'blue_top_total_gold',
    'blue_top_current_gold',
    'blue_top_cs',
    'blue_top_dmg_done',
    'blue_top_dmg_taken',
    'blue_jg_xp',
    'blue_jg_total_gold',
    'blue_jg_current_gold',
    'blue_jg_cs',
    'blue_jg_dmg_done',
    'blue_jg_dmg_taken',
    'blue_mid_xp',
    'blue_mid_total_gold',
    'blue_mid_current_gold',
    'blue_mid_cs',
    'blue_mid_dmg_done',
    'blue_mid_dmg_taken',
    'blue_bot_xp',
    'blue_bot_total_gold',
    'blue_bot_current_gold',
    'blue_bot_cs',
    'blue_bot_dmg_done',
    'blue_bot_dmg_taken',
    'blue_sup_xp',
    'blue_sup_total_gold',
    'blue_sup_current_gold',
    'blue_sup_cs',
    'blue_sup_dmg_done',
    'blue_sup_dmg_taken',
    'red_top_xp',
    'red_top_total_gold',
    'red_top_current_gold',
    'red_top_cs',
    'red_top_dmg_done',
    'red_top_dmg_taken',
    'red_jg_xp',
    'red_jg_total_gold',
    'red_jg_current_gold',
    'red_jg_cs',
    'red_jg_dmg_done',
    'red_jg_dmg_taken',
    'red_mid_xp',
    'red_mid_total_gold',
    'red_mid_current_gold',
    'red_mid_cs',
    'red_mid_dmg_done',
    'red_mid_dmg_taken',
    'red_bot_xp',
    'red_bot_total_gold',
    'red_bot_current_gold',
    'red_bot_cs',
    'red_bot_dmg_done',
    'red_bot_dmg_taken',
    'red_sup_xp',
    'red_sup_total_gold',
    'red_sup_current_gold',
    'red_sup_cs',
    'red_sup_dmg_done',
    'red_sup_dmg_taken',
]

def main():    
    ## keep a record of all matches that's been read
    cache_matches_filepath = os.path.join(os.path.dirname(__file__), '../dataset/matches.csv')

    cache_matches = set()
    with open(cache_matches_filepath, 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader, None)
        for _, _, match_id, _ in reader:
            cache_matches.add(match_id)
    
    # return
    # Scan for every csv in the `data/csv` folder
    # NOTE: for now, just open one to test
    csv_matches = []
    with os.scandir(os.path.join(os.path.dirname(__file__), '../data/csv')) as it:
        for entry in it:
            if entry.is_file() and entry.name.endswith('.csv'):
                with open(entry.path, 'r', newline='') as f:
                    print(entry.path)
                    reader = csv.reader(f)
                    next(reader, None)
                    csv_matches.extend(list(set([tuple(row) for row in reader if row[2] not in cache_matches])))
                    print(len(csv_matches))
    # Now open lol-data-matches.csv, which will hold the match id and the outcome of the match
    
    return
    version = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') 
    matches_filepath = os.path.join(
        os.path.dirname(__file__),
        '../output/csv/lol-data-matches-%s.csv' % version
    )
    frames_dir = os.path.join(
        os.path.dirname(__file__),
        '../output/csv/frames-%s' % (version)
    )
    error_filepath = os.path.join(
        os.path.dirname(__file__), 
        '../output/csv/lol-data-error-%s.csv' % version
    )
    if not os.path.exists(frames_dir):
        os.mkdir(frames_dir)

    # This is the start of the importing script. 
    # We open all three files for processing
    with open(matches_filepath, 'w', newline='') as (out
        ), open(error_filepath, 'w', newline='') as error_out:
        csv_match_out = csv.writer(out)
        csv_match_out.writerow(MATCH_DATA_HEADERS)
        error_out = csv.writer(error_out)
        error_out.writerow(['error'])

        # For displaying purposes, we keep note of the progress using the index
        for i, csv_match in enumerate(csv_matches):
            print("%i/%i" % (i+1, len(csv_matches)))

            try:
                # Fetch both match and timeline information from the Riot API   
                match = riot_api.get_match_by_matchid(csv_match[2])
                timeline = riot_api.get_match_timeline_by_matchid(csv_match[2])

                # Sometimes, the value of the match is empty. 
                # When this happens, skip the value.
                if match['info']['gameMode'] == '' or 'info' not in timeline: 
                    continue

                # Parse the match tuple, and append the division and the tier to its row
                match_id, frames, label = parse_sequence(timeline['info']['frames'], match)

                csv_match_out.writerow(csv_match + (label,))
                
                frame_filepath = os.path.join(
                    frames_dir,
                    '%s.csv' % (match_id)
                )

                with open(frame_filepath, 'w', newline='') as frame_out:
                    csv_frame_out = csv.writer(frame_out)
                    csv_frame_out.writerow(FRAME_DATA_HEADERS)
                    csv_frame_out.writerows(frames)
            except Exception as e:
                error_out.writerow([csv_match[2]])
                continue

if __name__ == "__main__":
    main()
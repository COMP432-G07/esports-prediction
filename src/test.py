from parsers.match_parser import parse_match
from parsers.timeline_parser import parse_sequence
import json

with open('../match.json') as f:
   frame_data = json.load(f)
with open('../match_details.json') as f:
   match_data = json.load(f)

match_id, frames, label = parse_sequence(frame_data['info']['frames'], match_data)

print(match_id, label)
import torch
import random

BLUE_PARTICIPANTS = ['1','2','3','4','5']
RED_PARTICIPANTS = ['6','7','8','9','10']

BLUE_SIDE = 0
RED_SIDE = 1

POS_DICT = {
    'TOP': 0,
    'JUNGLE': 1,
    'MIDDLE': 2,
    'BOTTOM': 3,
    'UTILITY': 4,
}

def get_total_gold(p):
    return p['totalGold']

def get_total_cs(p):
    return p['jungleMinionsKilled'] + p['minionsKilled']

def get_total_champion_damage(p):
    return p['damageStats']['totalDamageDoneToChampions']

def get_elite_monster_kills(monster_type, frames):
    kills = [e['killerTeamId'] for f in frames for e in f['events'] if e['type'] == 'ELITE_MONSTER_KILL' and e['monsterType'] == monster_type]
    return len([k for k in kills if k == 100]), len([k for k in kills if k == 200])

def get_champion_kills(frames):
    kills = [e['killerId'] for f in frames for e in f['events'] if e['type'] == 'CHAMPION_KILL']
    return len([k for k in kills if (str)(k) in BLUE_PARTICIPANTS]), len([k for k in kills if (str)(k) in RED_PARTICIPANTS])

def get_building_kills(building_type, frames):
    if building_type == 'TURRET_PLATE_DESTROYED':
        building_kills = [e['teamId'] for f in frames for e in f['events'] if e['type'] == building_type]
    else:
        building_kills = [e['teamId'] for f in frames for e in f['events'] if e['type'] == 'BUILDING_KILL' and e['buildingType'] == building_type]
    return len([k for k in building_kills if k == 200]), len([k for k in building_kills if k == 100])

# Parse frame takes a timeline's frame and creates a tuple
# containing all the relevant information that we wish to
# analyze, which includes each team's total gold, kills,
# cs, damage to champion, elite monster kills and 
# building kills
#
# Carry is used in order to figure the current tally of the particular
# stat line we are analyzing. Because the Timeline DTO is a collection
# of event, for a given frame number T and event type E, we accumulate
# every event E that has occured in Frames inside [0,T] for the sum.
#
# The tuple is returned such that in a numpy array, it can be reshaped into 
# a matric of size 2x10, allowing each corresponding statline to line
# up for to the counterpart (red_kills right on top of blue_kills,
# so on so forth...)
def parse_frame(match_id, timeline, frame_number):
    frame = timeline[frame_number]
    carry = timeline[:frame_number]
    
    # NOTE: id may not always be the same as `participantId`
    blue = [p for (id, p) in frame['participantFrames'].items() if (str)(p['participantId']) in BLUE_PARTICIPANTS]
    red = [p for (id, p) in frame['participantFrames'].items() if (str)(p['participantId']) in RED_PARTICIPANTS]

    # total gold
    red_gold = sum([get_total_gold(p) for p in red])
    blue_gold = sum([get_total_gold(p) for p in blue])

    # total CS (jungle + minions)
    red_cs = sum([get_total_cs(p) for p in red])
    blue_cs = sum([get_total_cs(p) for p in blue])

    # total damage to champions
    red_damage = sum([get_total_champion_damage(p) for p in red])
    blue_damage = sum([get_total_champion_damage(p) for p in blue])

    # elite monster kills (dragons, barons, rift heralds)
    blue_dragons, red_dragons = get_elite_monster_kills('DRAGON', carry)
    blue_barons, red_barons = get_elite_monster_kills('BARON_NASHOR', carry)
    blue_rift_heralds, red_rift_heralds = get_elite_monster_kills('RIFTHERALD', carry)

    # building kills (plates, towers, turret plates)
    blue_plates, red_plates = get_building_kills('TURRET_PLATE_DESTROYED', carry)
    blue_towers, red_towers = get_building_kills('TOWER_BUILDING', carry)
    blue_inhibitors, red_inhibitors = get_building_kills('INHIBITOR_BUILDING', carry)
    
    # champion kills
    blue_kills, red_kills = get_champion_kills(carry)

    return (
        match_id,
        frame_number,
        blue_kills,
        blue_gold,
        blue_cs,
        blue_damage,
        blue_towers,
        blue_plates,
        blue_inhibitors,
        blue_barons,
        blue_dragons,
        blue_rift_heralds,
        red_kills,
        red_gold,
        red_cs,
        red_damage,
        red_towers,
        red_plates,
        red_inhibitors,
        red_barons,
        red_dragons,
        red_rift_heralds
    )

def get_participant_role(match, participant_id):
    for p in match['info']['participants']:
        if p['participantId'] == participant_id:
            return p['individualPosition']

def get_participant(match, participant_id):
    teamSide = 0 if (str)(participant_id) in BLUE_PARTICIPANTS else 5

    position = next(p['individualPosition'] for p in match['info']['participants'] if p['participantId'] == participant_id)
    
    return POS_DICT[position] + teamSide

def preprocess_participant_frame(participantFrame, match):
    role = get_participant(match, participantFrame['participantId'])

    return (
        role,
        participantFrame['xp'],
        participantFrame['totalGold'],
        participantFrame['currentGold'],
        participantFrame['minionsKilled'] + participantFrame['jungleMinionsKilled'],
        participantFrame['damageStats']['totalDamageDone'],
        participantFrame['damageStats']['totalDamageTaken'],
    )

def get_winning_team(teams):
    team_id = next(m['teamId'] for m in teams if m['win'])
    return BLUE_SIDE if team_id == 100 else RED_SIDE

def parse_sequence(timeline, match):
    winning_team = get_winning_team(match['info']['teams'])
    match_id = match['metadata']['matchId']

    frames = []
    
    for frame in timeline:
        # What I want when preprocessing the frames
        participants = [preprocess_participant_frame(p, match) for (_, p) in frame['participantFrames'].items()]
        frames.append(sum([p[1:] for p in sorted(participants)], ()))
    
    return match_id, frames, winning_team
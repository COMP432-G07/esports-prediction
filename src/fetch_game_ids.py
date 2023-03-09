from services import riot_api
import csv
import os
import random

# You can configure these values in order
# to determine how much data you want to get
DIVISIONS = ['I','II','III','IV']
TIERS = {
    # 'BRONZE': (DIVISIONS,1250),
    # 'GOLD': (DIVISIONS,1250),
    # 'DIAMOND': (DIVISIONS,1250),
    'GRANDMASTERS': (['GR'], 50000)
}

# Get a list of game ids for the tiers specified above.
# Each tier holds a division. The algorithm is set
# such that an equal amount of match ids are 
# collected across each divisions equally.
#
def main():
    # First is setting up the api for a specific region
    # TODO: not gonna deal with this for now
    # api = new RiotAPI(REGION)
    csv_matches = []
    with os.scandir(os.path.join(os.path.dirname(__file__), '../data/csv')) as it:
        for entry in it:
            if entry.is_file() and entry.name.endswith('.csv'):
                with open(entry.path, 'r', newline='') as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    csv_matches.extend([tuple(row)[2] for row in reader])
    # return
    # Loop through the tiers from which 
    # we want to extract the games
    for tier, (divisions, thres) in list(TIERS.items()):    
        for division in divisions:
            with open(('lol-matches-%s-%s.csv' % (tier, division)), 'w', newline='') as out:
                csv_out = csv.writer(out)
                print("Completing %s %s matches" % (tier, division))
                # STAGE 1: Games collection for the tier
                matchIds = []
                # Pick up the players to look at
                players = riot_api.get_players_for_elo(tier=tier, division=division)
                # Shuffle the players to get a randomized choice of players
                random.shuffle(players)

                # Use this to see whether we reach the desired
                # amount of matches for a particular tier.
                carry = 0
                for summonerId in [p['summonerId'] for p in players]:
                    # Get the player's PUUID from his summoner record
                    summoner = riot_api.get_summoner_by_id(summonerId)
                    matches = riot_api.get_matches_by_puuid(summoner['puuid'], count=50)
                    filtered_matches = [(tier, division, m) for m in matches if m not in csv_matches]
                    # matchIds.extend(filtered_matches)
                    csv_out.writerows(filtered_matches)
                    # breakpoint()
                    carry += len(filtered_matches)
                    print("Completed %i out of %i matches" % (carry, thres)) 
                    if carry >= thres:
                        break

                # Matches are saved on an all-or-nothing basis. Hence, if the script 
                # fails, the script must be restarted. Each tier and division is
                # saved separately; for DIAMOND I, the games will be saved
                # inside (lol-matches-DIAMOND-I.csv)
                # with open(('lol-matches-%s-%s.csv' % (tier, division)), 'w', newline='') as out:
                #     csv_out = csv.writer(out)
                #     csv_out.writerows(matchIds)

    
if __name__ == "__main__":
    main()
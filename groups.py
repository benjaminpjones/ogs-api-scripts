import requests
import json
import datetime
import time

def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def last_game_ended_timestamp(player_id):
    time.sleep(15)
    player_games_response = requests.get("https://online-go.com/api/v1/players/{}/games/?ended__isnull=false&ordering=-ended&source=play".format(admin['id']))

    try:
        return player_games_response.json()['results'][0]['ended']
    except KeyError as err:
        print("KeyError, player: {}, status code: {}".format(player_id, player_games_response.status_code))
        return None
    except IndexError as err:
        print("IndexError: No games played, player: {}".format(player_id))
        return None

all_groups_file = open("all_groups.txt", "w")
stale_admin_file = open("stale_admins.txt", "w")


response = requests.get("https://online-go.com/api/v1/groups/?ordering=-member_count")

ctr = 1
while True:
  for group in response.json()['results']:
    group_info = group['name'] + '\n'

    if group['hide_details'] == True:
        group_info += '    Details hidden\n'
        continue

    group_detail_response = requests.get("https://online-go.com/api/v1/groups/{}".format(group['id']))

    latest_played_year = 0
    for admin in group_detail_response.json()['admins']:
        last_game = last_game_ended_timestamp(admin['id'])
        year = int(last_game[:4]) if last_game else 0
            
        latest_played_year = max(year, latest_played_year)
        group_info += '    {} {}\n'.format(admin['username'], last_game)

    all_groups_file.write(group_info)
    stale = False
    if latest_played_year < 2020:
        stale = True
        stale_admin_file.write(group_info)

    print(ctr, group_info)
    print('    ', 'STALE' if stale else 'CURRENT')
    ctr += 1

  if not response.json()['next']:
    break
  response = requests.get(response.json()['next'])

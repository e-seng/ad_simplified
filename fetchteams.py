#!/usr/bin/env python3
import argparse

### START COPYING HERE ###
import requests
import time
import traceback
import sys

def run_on_teams(exploit: "function(host: str, port: int, data: str)",
                 challenge_name: str, # matches the name on teams.json
                 challenge_port: int, # the port team_iding the challenge
                 exploiter_team_id: str, # your team id
                 team_json_url="https://2023.faustctf.net/competition/teams.json", # the url to get team and tick information, assuming faust format
                 team_id_format=None, # a string to format with the team id provided in teams.json. this will replace "<team-number" within the string
                 json_timeout=10, # teams.json timeout, in seconds
                 tick_duration=120, # time between ticks, in seconds
                 nop_only=False, # exploit against only the nop team, likely the first team within teams.json
                 verbose=True, # print progress information
                 debug=False, # print developer information
                ):
    team_info = None

    if(verbose):
        print(f"[*] fetching team data from {team_json_url}... ", end="")

    try:
        team_info = requests.get(team_json_url, timeout=json_timeout).json()
    except ConnectionError as e:
        if(verbose): print("failed - connection error")
    except Timeout as e:
        if(verbose): print("failed - timeout")
    except Exception as e:
        if(verbose): print("failed - general exception :)")

    if(verbose): print("done!")
    if(debug): print(f"[?] team_info = {team_info}")

    while(True):
        start_time = int(time.time())

        if(verbose): print("[*] exploiting this tick")
        for team_id in team_info["teams"]: # get each team
            team_id = str(team_id) # json and things use strings, properly convert
            if(team_id == exploiter_team_id): continue # do not exploit self

            # generate the host to exploit, unless the team id is the team host
            host = (team_id_format.replace("<team-number>", team_id)
                if team_id_format is not None else team_id)
            if team_id not in team_info["flag_ids"][challenge_name].keys():
                if(debug): print(f"[!] could not find flag info for team {team_id}."\
                    "skipping...")
                continue

            for tick, data in enumerate(
                    team_info["flag_ids"][challenge_name][team_id]):
                # properly format the team_id address
                if team_id_format is not None:
                    team_id = team_id_format.replace("<team-number>", team_id)
                try:
                    exploit(host, challenge_port, data)
                except Exception as e:
                    if(not verbose): continue
                    print(f"[!] exploit failed! please see the following"\
                          " traceback")
                    print(traceback.format_exc())
            # nop team is typically at the top of the list of teams.json
            if(nop_only): break
        if(verbose): print(f"[*] finished exploitation for this tick")

        # wait for next tick
        time_elapsed = int(time.time()) - start_time # sync with clock
        if(not verbose):
            sleep(tick_duration - time_elapsed)
            continue

        print("[*] sleeping for ", end="")
        for _ in range(tick_duration - time_elapsed):
            minutes = (tick_duration - time_elapsed) // 60 # seconds in a minute
            seconds = (tick_duration - time_elapsed) % 60 # seconds in a minute
            countdown = f"{minutes:02}:{seconds:02}"
            sys.stdout.write(countdown)
            sys.stdout.flush()
            time.sleep(1) # countdown each second
            sys.stdout.write('\b'*(len(countdown)))
            time_elapsed = int(time.time()) - start_time # update elapsed time
        print("done!")
    return

### END COPYING HERE ###

def example_exploit(host, port, param):
    if(host == "fd66:666:971::2"): raise Exception("I'm a test exception wooooo")
    print(f"[test] exploiting {host}:{port} with the following data: {param}")
    pass

if __name__ == "__main__":
    run_on_teams(example_exploit,
                 "Notes from the Future",
                 1337,
                 248,
                 nop_only=True,
                 team_json_url="https://2022.faustctf.net/competition/teams.json",
                 team_id_format="fd66:666:<team-number>::2",
                 verbose=True,
                 debug=False,
                )
#!/usr/bin/env python
from __future__ import print_function
import sys
import argparse

from time import sleep
from monitorpubg import PUBGPlayerMonitor


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-p', '--pubg_api_key', required=True, help="PUBG Tracker API key", type=str)
    parser.add_argument('-s', '--slack_token', required=True, help="Slack Bot token", type=str)
    parser.add_argument('-c', '--slack_channel', required=True, help="Slack channel", type=str)
    parser.add_argument('-e', '--pubg_season', required=True, help="PUBG Season", type=str)
    parser.add_argument('-m', '--players_monitored', required=True, help="Players monitored", type=str)

    args = parser.parse_args(arguments)
    players = args.players_monitored.split(',')
    pm = PUBGPlayerMonitor(pubg_api_key=args.pubg_api_key,
                           slack_token=args.slack_token,
                           slack_channel=args.slack_channel,
                           season=args.pubg_season,
                           players_monitored=players)

    pm.slack_message("#pubgtrackerbot", "Starting to monitor...\nPlayers: {0}\nSeason: {1}".format(players.join(','), args.pubg_season))

    while 1:
        pm.slack_message("#pubgtrackerbot", "Checking player wins.")
        pm.check_player_wins()
        sleep(30)
        pm.check_match_history()
        pm.slack_message("#pubgtrackerbot", "Checking player match history.")
        sleep(30)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

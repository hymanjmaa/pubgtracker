#!/usr/bin/env python
from __future__ import print_function
import sys
import argparse

from time import sleep
from datetime import datetime
from monitorpubg import PUBGPlayerMonitor


def main(arguments):

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-p', '--pubg_api_key', required=True, help="PUBG Tracker API key", type=str)
    parser.add_argument('-s', '--slack_token', required=True, help="Slack Bot token", type=str)
    parser.add_argument('-c', '--slack_channel', required=True, help="Slack channel", type=str)
    parser.add_argument('-m', '--players_monitored', required=True, help="Players monitored", type=str)

    args = parser.parse_args(arguments)
    players = args.players_monitored.split(',')
    pm = PUBGPlayerMonitor(pubg_api_key=args.pubg_api_key,
                           slack_token=args.slack_token,
                           slack_channel=args.slack_channel,
                           players_monitored=players)

    pm.slack_message("#pubgtrackerbot", "Starting to monitor...\nPlayers: {0}".format(args.players_monitored))

    while 1:
        now = datetime.now()
        pm.check_player_agg_wins()
        if now.minute % 15 == 0:
            pm.slack_message("#pubgtrackerbot", "PUBG Stat Tracker is running. See current stats monitored for all "
                                                "players below.")
            for player_stats in pm.player_agg_stats:
                pm.slack_message("#pubgtrackerbot", "Player: {0}\nStats:\n{1}".format(player_stats['player'], player_stats))

        sleep(15)



if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

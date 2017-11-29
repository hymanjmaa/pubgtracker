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
    parser.add_argument('-m', '--players_monitored', required=True, help="Players monitored", type=str)

    args = parser.parse_args(arguments)
    players = args.players_monitored.split(',')
    pm = PUBGPlayerMonitor(api_key=args.pubg_api_key,
                           players_monitored=players,
                           slack_token=args.slack_token)
    while 1:
        pm.check_player_agg_stats()
        sleep(15)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

#!env/bin/python
from os import getenv as environ
from time import sleep
from monitorpubg import PUBGPlayerMonitor


def main():
    pm = PUBGPlayerMonitor(pubg_api_key=environ("PUBGAPI_KEY"),
                           slack_token=environ("SLACK_TOKEN"),
                           slack_channel="pubg",
                           season="2017-pre3",
                           players_monitored=["summit1g", "shroud", "MrGrimmmz"])
    while 1:
        pm.check_player_wins()
        sleep(1)
        pm.check_match_history()
        sleep(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env bash

tar -xf pubgtracker_build.tar.gz
source venv/bin/activate
python monitor.py -p ${PUBG_API_KEY} -s ${SLACK_TOKEN} -c ${SLACK_CHANNEL} -e ${PUBG_SEASON} -m ${PLAYERS_MONITORED}
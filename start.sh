#!/usr/bin/env bash

cd /home/ec2-user
pwd > /tmp/build.out
ls >> /tmp/build.out
source venv/bin/activate
python monitor.py -p ${PUBG_API_KEtail Y} -s ${SLACK_TOKEN} -c ${SLACK_CHANNEL} -e ${PUBG_SEASON} -m ${PLAYERS_MONITORED}
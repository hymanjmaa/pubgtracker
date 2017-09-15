#!/usr/bin/env bash

cd /home/ec2-user

export PUBG_API_KEY=`aws ssm get-parameters --names PUBG_API_KEY --region us-west-2 --with-decryption --query 'Parameters[0].Value' --output text`
export SLACK_TOKEN=`aws ssm get-parameters --names SLACK_TOKEN --region us-west-2 --with-decryption --query 'Parameters[0].Value' --output text`
python35 monitor.py -p ${PUBG_API_KEY} -s ${SLACK_TOKEN} -c "#pubg" -m "iabosi,GlochNessMonster,TheKroniuss,SPLASH5,viceversus,AstroCreep,PumpActionCame," > output.log 2>&1 &
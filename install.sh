#!/usr/bin/env bash
cd /home/ec2-user
sudo yum -y update
sudo yum -y install python35 python35-pip
sudo pip-3.5 install -r requirements.txt

#!/usr/bin/env bash
sudo yum -y update
sudo yum -y install python35
sudo yum -y install python35-pip
sudo pip-3.5 install -r requirements.txt
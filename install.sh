#!/bin/bash

# If MergeList error on apt update
#sudo mv /var/lib/apt/lists /var/lib/apt/oldlists
#sudo apt clean
sudo apt update
sudo apt install python3-pip
sudo pip install -r requirements.txt  --break-system-packages

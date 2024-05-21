#!/bin/bash
echo "Running the web player" >> piano.log 
chmod 666 piano.log
#Requires sudo for GPIO
sudo python3 -u web-player-v3.py  >> piano.log 2>&1 
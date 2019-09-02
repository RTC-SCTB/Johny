#!/bin/sh
sudo ip link set can0 up type can bitrate 500000
./onboard.py
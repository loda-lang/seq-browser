#!/bin/bash

export PATH=$PWD/venv/bin:$PATH

echo "Restarting seq-browser"
killall flask 2> /dev/null
nohup flask --app seq-browser run > seq-browser.out 2>&1 &

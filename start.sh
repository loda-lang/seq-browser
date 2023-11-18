#!/bin/bash

export PATH=$PWD/venv/bin:$PATH
nohup flask --app seq-browser run > seq-browser.out 2>&1 &

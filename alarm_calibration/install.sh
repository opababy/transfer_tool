#!/bin/sh

SRC_DIR=$(dirname $(realpath $0))
mkdir -p /tmp/SD0/MISC/
cp -v $SRC_DIR/event_fusion.json /tmp/SD0/MISC/event_fusion.json

# only run the set_roi_window part of event_fusion
/usr/local/share/script/event_callback.py -C /tmp/SD0/MISC/event_fusion.json -i /dev/INVALID_DEV

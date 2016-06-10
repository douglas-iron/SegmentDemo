#!/bin/sh
IMAGE=$1
PAYLOAD=$2

docker run --rm -v "/$PWD"://worker -e "PAYLOAD_FILE=//worker/$PAYLOAD" $IMAGE

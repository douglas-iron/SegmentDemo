#!/bin/sh

DOCKER=$1
IMAGE=$2
VERFILE="seg.ver.txt"
VER=`cat $VERFILE | grep -E "$DOCKER=" | grep -Eoh "[0-9]+\.[0-9]+"`
PYTHON=$3
PAYLOAD=$4
TEST=$5

echo $DOCKER
echo $IMAGE
echo $VER
echo $PYTHON
echo $PAYLOAD
echo $TEST

if [ -z $DOCKER ] || [ -z $IMAGE ] || [ -z $PYTHON ] || [ -z $PAYLOAD ] || [ -z $TEST ]; then
	echo "Usage: ./runBuild.sh Dockerfile.Name username/image x.yy python-name.py payload.json 1"
	echo "This script allows you to either build a Docker contianer and then run it or build it and publish it"
	echo ""
	echo "Dockerfile: The docker file that has the information for the docker container"
	echo "ImageName: The docker image name, like user/myimage for Docker hub"
	echo "version: The version tag, recommended to be something like 0.10"
	echo "PythonFile: The name of the python file to get from the parent folder"
	echo "payload: The name of the payload file"
	echo "Test: 1 means build and test, 0 means build and publish"
	exit 1
fi

if [ $TEST -eq 1 ]; then
	rm -rf *.py
	rm -rf iron.json
	cp ../$PYTHON ./
	cp ../iron.json ./
	docker rmi $IMAGE:$VER
	docker build -f Dockerfile.$DOCKER -t $IMAGE:$VER .
	docker run --rm -v "/$PWD:/worker" -e "PAYLOAD_FILE=//worker/$PAYLOAD" $IMAGE:$VER
elif [ $TEST -eq 0 ]; then
	rm -rf *.py
	rm -rf iron.json
	cp ../$PYTHON ./
	cp ../iron.json ./
	docker rmi $IMAGE:$VER
	docker build -f Dockerfile.$DOCKER -t $IMAGE:$VER .
	docker push $IMAGE:$VER
	if [ `echo $docker | grep -q Master` ]; then
		iron register --max-concurrency 1 $IMAGE:$VER
	else
		iron register $IMAGE:$VER
	fi
fi

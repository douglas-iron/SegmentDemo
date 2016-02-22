#!/bin/sh
rm segmentWorker.zip
zip -r segmentWorker.zip -x@exclude.lst . 
iron worker upload -zip segmentWorker.zip -name segment iron/python:2 python segmentWorker.py

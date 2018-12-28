#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys
import os
import openslide
import cv2 as cv

def getRect(positions):
	x_s = [];
	y_s = [];
	for length in range(0,len(positions)):
		x_s.append(positions[length][0]);
		y_s.append(positions[length][1]);
	x_min = min(x_s);
	x_max = max(x_s);
	y_min = min(y_s);
	y_max = max(y_s);
	return (x_min,y_min,x_max-x_min,y_max-y_min);

def readRegionsFromXml(xmlFileName):
	srcHandle = open(xmlFileName,'r');
	srcString = srcHandle.read();
	strArray = srcString.split("\n");
	regions = [];
	regionId = 0;
	recordStart = False;
	for line in range(0,len(strArray)):
		# print(strArray[line].lstrip());
		current = strArray[line].lstrip();
		if current == '</Vertices>':
			# record end
			regionId +=1;
			recordStart = False;
		if recordStart:
			current = current.replace('"','');
			coordirate = current.split(" ");
			# print(coordirate);
			x = int((coordirate[1].split("="))[1]);
			y = int((coordirate[2].split("="))[1]);
			regions[regionId].append((x,y));
		if current == '<Vertices>':
			# record start
			recordStart = True;
			regions.append([]);

	# print(len(regions));
	rects = [];
	for regionId in range(0,len(regions)):
		rect = getRect(regions[regionId]);
		rects.append(rect);
	return rects;

def main(argv):
	xmlFileName = argv[1];
	targetRects = readRegionsFromXml(xmlFileName);
	slide = openslide.OpenSlide(argv[2]);
	for rect in targetRects:
		targetImage = slide.read_region((rect[0],rect[1]),0, (rect[2],rect[3]),3);
		path = os.path.join("D:\Lymph_Follicle",str(rect)+".png");
		cv.imwrite(path,targetImage);
	
if __name__ == '__main__':
    main(sys.argv)








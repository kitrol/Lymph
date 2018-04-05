#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import openslide
import sys
import os
import numpy as np
import cv2 as cv
def wirteTrainDataToFile(targetFileName,rgbData,singleDataSize):
	file = open(targetFileName, "w+");
	string = '';
	for index in range(len(rgbData)):
		string += "%d,%d,%d\n"%(rgbData[index][0],rgbData[index][1],rgbData[index][2]);
	file.write(string);
	file.close();

def main(argv):
	# read marked train image
	targetFileName_ = argv[1];
	print(targetFileName_);
	train_data = cv.imread(targetFileName_);
	print(train_data.shape);
	width = train_data.shape[0];
	height = train_data.shape[1];
	positive_sample = [];
	nagitave_sample = [];
	sampleKernelSize = 5;
	offset = int((sampleKernelSize-1)/2);
	###real size is 5*5
	# * * * * *
	# * * * * *
	# * * * * *
	# * * * * *
	# * * * * *
	# separate the positive samples and nagitave samples
	for x in range(offset,width-offset):
		for y in range(offset,height-offset):
			targetPixel = train_data[x][y];
			if (targetPixel==np.array([0,0,0])).all():
				positive = train_data[x-offset:x+offset,y-offset:y+offset,:];
				positive.reshape([sampleKernelSize*sampleKernelSize,1,train_data.shape[2]]);
				positive_sample.append(positive);
			elif (targetPixel==np.array([0,0,255])).all():
				nagitave = train_data[x-offset:x+offset,y-offset:y+offset,:];
				nagitave.reshape([sampleKernelSize*sampleKernelSize,1,train_data.shape[2]]);
				nagitave_sample.append(nagitave);
	# write the samples to file
	
	wirteTrainDataToFile();

if __name__ == '__main__':
   main(sys.argv);
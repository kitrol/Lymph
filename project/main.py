#!/usr/bin/python
# -*- coding: UTF-8 -*- 
import cv2 as cv
import numpy as np
import sys
import os
import subprocess
import platform

import globalVal as gl
import processOneImage as ps
import createNewTestData as cntd
import detectiveLymph as dl



def scanTrainFolder(folderFullName):
	targetFileName = [];
	fileNameList = [];
	returnDict = {};
	for parent,dirnames,filenames in os.walk(folderFullName):
		for filename in filenames:
			filePrex = filename.split(".")[0];
			index = filePrex.find("_correct");
			if index==-1:
				targetFileName.append(filePrex);
			fileNameList.append(filePrex);
	
	for filename in targetFileName:
		for x in fileNameList:
			if filename+"_correct" == x:
				returnDict[filename+'.bmp'] = x+'.bmp';
		
	return returnDict;


def main(argv):
	gl.initDir(argv);
	#  START 
	#*******   get setdata from train data ************
	print("*******   get setdata from train data ************");
	pairs = scanTrainFolder(gl.TrainFolder);
	# orgImageName = "JF15_022_2_HE.bmp";
	# correctImageName = "JF15_022_2_HE_correct.bmp";
	# ps.processOneTrainImage(orgImageName,correctImageName);
	print("*******   prepare new test data by setdata ************");
	# for item in pairs:
	# 	print(item+" : "+pairs[item]);
	# 	ps.processOneTrainImage(item,pairs[item]);
	#*******   prepare new test data by setdata ************

	# cntd.getNewTestData("JF14_092_S8_HE.bmp","JF14_091_S8_HE_notWhiteAvg&Var.txt");
	print("*******   detect the lymph follicle from new test data ************");
	#*******   detect the lymph follicle from new test data ************

	# dl.detectiveLymphFromNewTestData("JF14_092_S8_HE_new.bmp","JF15_022_2_HE_region.csv","JF15_022_2_HE_regionAvg&Var.txt");
	dl.detectiveLymphFromNewTestData("JF15_022_2_HE.bmp","JF15_022_2_HE_region.csv","JF15_022_2_HE_regionAvg&Var.txt",True);
	#*******  Dinish ************

if __name__ == '__main__':
   main(sys.argv)
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
from array import array

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
	# print(gl.worktDir_);
	# img = cv.imread(r'C:\Users\kitrol\Desktop\moto_1.bmp');
	# ret,img = cv.threshold(img,0,255,cv.THRESH_BINARY); # 反转颜色 黑色区域变白，其他区域变黑 CV_THRESH_BINARY_INV|CV_THRESH_OTSU
	# check_img = np.zeros(img.shape,img.dtype);
	# check_img[::] = 255;
	# # check = np.zeros((5,5,3),img.dtype);
	# ps.showImageInWindow('1',10000,img);

	#  START 

	pairs = scanTrainFolder(gl.TrainFolder);
	# print(pairs);
	# orgImageName = "JF15_022_2_HE.bmp";
	# correctImageName = "JF15_022_2_HE_correct.bmp";
	# ps.processOneTrainImage(orgImageName,correctImageName);

	
	getNewTestData("JF14_092_S8_HE.bmp","JF14_091_S8_HE_notWhiteAvg&Var.txt");
	dl.detectiveLymphFromNewTestData();

	# x = np.array([[3,4],[5,6],[2,2],[8,4]]);
	# xT=x.T;
	# D=np.cov(xT);
	# invD=np.linalg.inv(D);
	# tp=x[0]-x[1];
	# print(tp);
	# print(invD);
	# print(np.sqrt(np.dot(np.dot(tp,invD),tp.T)));


	# for (original,corrent) in pairs.items():
	# 	ps.processOneTrainImage(original,corrent);


	# meanArray = np.array([123,456,223]);
	# variance = np.array([12,56,123]);
	# result = {"meanArray":list(meanArray),"variance":list(variance)};
	# print(str(result));
	# file = open(gl.worktDir_+gl.TextFolder+"testOutput.txt", "w+");
	# file.write(str(result));
	# file.close();


if __name__ == '__main__':
   main(sys.argv)
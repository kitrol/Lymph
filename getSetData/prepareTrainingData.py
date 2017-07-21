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
	img = cv.imread(r'C:\Users\kitrol\Desktop\moto_1.bmp');
	ret,img = cv.threshold(img,0,255,cv.THRESH_BINARY); # 反转颜色 黑色区域变白，其他区域变黑 CV_THRESH_BINARY_INV|CV_THRESH_OTSU
	check_img = np.zeros(img.shape,img.dtype);
	check_img[::] = 255;
	# check = np.zeros((5,5,3),img.dtype);

	
	ps.showImageInWindow('1',10000,img);

	# pairs = scanTrainFolder(gl.TrainFolder);
	# print(pairs);
	# # orgImageName = "JF14_091_S8_HE.bmp";
	# # correctImageName = "JF14_091_S8_HE_correct.bmp";
	# # ps.processOneTrainImage(orgImageName,correctImageName);
	# for (original,corrent) in pairs.items():
	# 	ps.processOneTrainImage(orgImageName,correctImageName);


	# result = {"meanArray":[123,456,223],"variance":[12,56,123]};
	# print(str(result));
	# file = open(gl.worktDir_+gl.TextFolder+"testOutput.txt", "w+");
	# file.write(str(result));
	# file.close();

	# file = open(gl.worktDir_+gl.TextFolder+"testOutput.txt", "r");
	# string = file.read();
	# dict_1 = eval(string);
	# print(dict_1);
	# file.close();
	# print(type(dict_1['meanArray'][0]));

if __name__ == '__main__':
   main(sys.argv)
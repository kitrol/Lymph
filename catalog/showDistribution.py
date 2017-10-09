#!/usr/bin/python
# -*- coding: UTF-8 -*- 
#created by liangj


import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
import platform
import os
import math

currentDir_ = "";
colorLevel_ = "";


def iniDir(argv):
	global currentDir_;
	currentDir_ = os.path.dirname(argv[0]);
	sysstr = platform.system();
	if sysstr == "Windows":
		currentDir_ += "\\";
		colorLevel_ = currentDir_ + "separateByColorLevel\\";
	else:
		currentDir_ += "/";
		colorLevel_ = currentDir_ + "separateByColorLevel/";
	print("Working Dir is "+currentDir_);

def showPicForData(targetData):
	#  prepare for the data to draw
	paintData_1 = [];
	paintData_0 = [];
	for item in targetData:
		if int(item[4]) == 1:
			paintData_1.append([item[1],item[2],item[3]]);
		else:
			paintData_0.append([item[1],item[2],item[3]]);

	paintData_0 = np.array(paintData_0);
	paintData_1 = np.array(paintData_1);
	# plot pic for data
	fig = plt.figure();
	ax = fig.add_subplot(1,1,1, projection='3d');
	ax=plt.subplot(111,projection='3d');
	ax.scatter(paintData_0[::,0],paintData_0[::,1],paintData_0[::,2],c='b');
	ax.scatter(paintData_1[::,0],paintData_1[::,1],paintData_1[::,2],c='r');
	ax.set_zlabel('height'); 
	ax.set_ylabel('weight');
	ax.set_xlabel('age');
	plt.show();


def showImageInWindow(windowName,time,image):
	cv.namedWindow(windowName,cv.WINDOW_NORMAL);
	cv.imshow(windowName,image);
	cv.waitKey(time);
	cv.destroyAllWindows();

def minusAverage(image):
	global currentDir_;
	originalImage = cv.imread(currentDir_+"JF15_022_2_HE_gray.bmp",1);
	grayImageWhole = cv.imread(currentDir_+"JF15_022_2_HE_gray.bmp",0);
	for width in range(0,opening.shape[0]):
		for height in range(0,opening.shape[1]):
			if opening[width,height]==0:
				grayImageWhole[width,height]=255; 

def separateColor(image):
	global colorLevel_;
	print(image.shape);
	channel = 2;
	minRed = image[:,:,channel].min();
	maxRed = image[:,:,channel].max();
	print("minRed is %d maxRed is %d "%(minRed,maxRed));
	# newImage = np.zeros(image.shape,dtype=np.uint8);
	# newImage[::] = 255;
	# print(newImage[:,:,1].max());

	redRange = maxRed-minRed;
	interval = 10.0;
	groups = int(math.ceil(redRange/interval));
	print(groups);
	for group in range(1,groups):
		newImage = np.zeros(image.shape,dtype=np.uint8);
		newImage[::] = 255;
		groupRangeMin = (group-1)*interval+minRed;
		groupRangeMax = group*interval+minRed;
		for height in range(0,image.shape[0]):
			for weight in range(0,image.shape[1]):
				if ( (image[height,weight,channel] >= groupRangeMin) and (image[height,weight,channel] < groupRangeMax)):
					newImage[height,weight] = image[height,weight];
		cv.imwrite(colorLevel_+"JF14_091_S8_HE_group%d.bmp"%(group),newImage);

def main(argv):
	iniDir(argv);

	global currentDir_;
	fileName = currentDir_+"JF14_091_S8_HE.png";# JF14_091_S8_HE-2.png 
	colorImage = cv.imread(fileName);
	separateColor(colorImage);





	# grayImage = cv.imread(fileName,0);
	# blur = cv.GaussianBlur(grayImage,(5,5),0);
	# blur2 = cv.GaussianBlur(blur,(5,5),0);
	# ret2,grayImage2 = cv.threshold(grayImage,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU);
	# width=grayImage.shape[0];
	# height=grayImage.shape[1];

	
	# originalGrayImage = cv.imread(currentDir_+"JF15_022_2_HE.bmp",0);
	# ret1,regionImage = cv.threshold(originalGrayImage,0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU);# THRESH_BINARY_INV THRESH_BINARY
	# cv.imwrite(currentDir_+"JF15_022_2_HE_Black.bmp",regionImage);

	# kernel = np.ones((3,3),np.uint8);
	# opening = cv.morphologyEx(regionImage, cv.MORPH_OPEN, kernel);
	# cv.imwrite(currentDir_+"JF15_022_2_HE_open.bmp",opening);



	# grayImageWhole = cv.imread(currentDir_+"JF15_022_2_HE_gray.bmp",0);
	# grayValueaArray = [];
	# for width in range(0,opening.shape[0]):
	# 	for height in range(0,opening.shape[1]):
	# 		if opening[width,height]==0:
	# 			grayImageWhole[width,height]=255; 
	# 		else:
	# 			grayValueaArray.append(grayImageWhole[width,height]);


	# grayVector = np.array(grayValueaArray);

	# blur4 = cv.GaussianBlur(grayImageWhole,(5,5),0);
	# blur4 = cv.GaussianBlur(blur4,(5,5),0);
	# print(grayImageWhole.shape);
	# sub = blur4[300];
	# plt.plot(sub)
	# plt.ylabel('gray')
	# plt.show();
	# cv.imwrite(currentDir_+"JF15_022_2_HE_gray_2.bmp",grayImageWhole);
	# cv.imwrite(currentDir_+"JF15_022_2_HE_gray_2_blur4.bmp",blur4);
	
	# blur3 = cv.GaussianBlur(opening,(5,5),0);
	# cv.imwrite("D:\Lymph_Follicle\python\catalog\JF15_022_2_HE_blur3.bmp",blur3);

	# cv.imwrite("D:\Lymph_Follicle\python\catalog\JF14_091_S8_HE_gray.bmp",grayImage);
	# cv.imwrite("D:\Lymph_Follicle\python\catalog\JF14_091_S8_HE_blur.bmp",blur);
	# cv.imwrite("D:\Lymph_Follicle\python\catalog\JF14_091_S8_HE_blur2.bmp",blur2);
	# cv.imwrite("D:\Lymph_Follicle\python\catalog\JF14_091_S8_HE_gray2.bmp",grayImage2);

	# sub = blur2[:,26];
	# plt.plot(sub)
	# plt.ylabel('gray')
	# plt.show();
	# print(sub);
	# print(grayImage.shape);

if __name__ == '__main__':
   main(sys.argv)
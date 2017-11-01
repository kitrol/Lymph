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
import time
from skimage import io,measure,color

currentDir_ = "";
colorLevel_ = "";
sysstr_ = "";
COLORFULL = 1;
GRAY = 0;
interval = 8;
channel = 2; # color channel B:0 G:1 R:2s
kernel = (15,15);

def iniDir(argv):
	global currentDir_;
	global colorLevel_;
	global sysstr_;
	currentDir_ = os.path.dirname(argv[0]);
	sysstr_ = platform.system();
	if sysstr_ == "Windows":
		currentDir_ += "\\";
		colorLevel_ = currentDir_ + "separateByColorLevel\\";
	else:
		currentDir_ += "/";
		colorLevel_ = currentDir_ + "separateByColorLevel/";
	print("Working Dir is "+currentDir_);

def getRelativeDir(folderNamesArray):
	global currentDir_;
	relativeDir = currentDir_;
	for folderName in folderNamesArray:
		relativeDir += folderName;
		if sysstr_ == "Windows":
			relativeDir += "\\";
		else:
			relativeDir += "/";
	return relativeDir;

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

def addColor(color,addNum):
	if (color+addNum)>255:
		return 255;
	elif (color+addNum)<0:
		return 0;
	else:
		return color+addNum;

def sharpProcess(image):
	global currentDir_;
	global channel;

	for height in range(0,image.shape[0]-1):
		for width in range(0,image.shape[1]-1):
			colorLeft = image[height,width,channel];
			colorRight = image[height,width+1,channel];
			value_ = abs(int(colorLeft)-int(colorRight));
			if (max(colorLeft,colorRight) != 255) and (value_ > 20) :
				if image[height,width,channel] > image[height,width+1,channel]:
					image[height,width,channel] = min(255,image[height,width,channel]+30);
					image[height,width+1,channel] = max(0,image[height,width+1,channel]-30);
				else:
					image[height,width,channel] = max(0,image[height,width,channel]-30);
					image[height,width+1,channel] = min(255,image[height,width+1,channel]+30);
	return image;

def blurForChannels(colorImage,channelID=None):
	channels = colorImage.shape[2];
	global kernel;
	if channelID:
		colorImage[:,:,channelID] = cv.GaussianBlur(colorImage[:,:,channelID],kernel,0);
	else:
		for channel in range(0,channels):
			colorImage[:,:,channel] = cv.GaussianBlur(colorImage[:,:,channel],kernel,0);
	return colorImage;

def getImageWithBlackBg(image):
	global channel;
	ret,regionImage = cv.threshold(image[:,:,channel],0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU);
	return regionImage;

def filterImageByBlackImage(originalImage,maskImage):
	# mask image should be white and black,the background of the originalImage should be black 
	# in maskImage and the tissue regions should be white.
	for height in range(0,maskImage.shape[0]):
		for width in range(0,maskImage.shape[1]):
			if maskImage[height,width]==0:
				originalImage[height,width,:]=255;

	return originalImage;

def reduceNoise(originImage):
	newImage = np.zeros(originImage.shape,dtype=np.uint8);
	newImage[::] = 255;
	for height in range(0,originImage.shape[0]):
		for weight in range(0,originImage.shape[1]):
			if max(originImage[height,weight]) - min(originImage[height,weight]) > 20:
				newImage[height,weight] = originImage[height,weight];
	return newImage;

def separateColor(image,outputFormat,outputDir):
	print("Func separateColor: oringin image size is");
	print(image.shape);
	global channel; #  RED channel
	pixels = [];
	minInChannel = 255;
	maxInChannel = 0;
	for height in range(0,image.shape[0]):
		for weight in range(0,image.shape[1]):
			if (image[height,weight]==np.array([255,255,255])).all():
				continue;
			else:
				if minInChannel > image[height,weight,channel]:
					minInChannel = image[height,weight,channel];
				if maxInChannel < image[height,weight,channel]:
					maxInChannel = image[height,weight,channel];
	# print("minInChannel is %d maxInChannel is %d "%(minInChannel,maxInChannel));				
	colorRange = maxInChannel-minInChannel;
	global interval;
	groups = int(math.ceil(colorRange/interval));
	print("groups is %d "%(groups));

	outputImages = [];
	boundaries = [];
	for group in range(0,groups):
		newImage = np.zeros(image.shape,dtype=np.uint8);
		newImage[::] = 255;
		outputImages.append(newImage);
		groupRangeMin = group*interval+minInChannel;
		groupRangeMax = (group+1)*interval+minInChannel;
		boundaries.append((groupRangeMin,groupRangeMax));

	# for group in range(0,groups):
	# 	newImage = np.zeros(image.shape,dtype=np.uint8);
	# 	newImage[::] = 255;
	# 	# groupRangeMin = (group-1)*interval+minInChannel;
	# 	# groupRangeMax = group*interval+minInChannel;
	# 	groupRangeMin = boundaries[group][0];
	# 	groupRangeMax = boundaries[group][1];
	# 	for height in range(0,image.shape[0]):
	# 		for weight in range(0,image.shape[1]):
	# 			if (image[height,weight]==np.array([255,255,255])).all():
	# 				continue;
	# 			elif ( (image[height,weight,channel] >= groupRangeMin) and (image[height,weight,channel] < groupRangeMax) and (max(image[height,weight]) - min(image[height,weight]) > 10) ):
	# 				newImage[height,weight] = image[height,weight];
	# 	cv.imwrite(outputDir+outputFormat%(group),newImage);

	for height in range(0,image.shape[0]):
		for weight in range(0,image.shape[1]):
			pixelColor = image[height,weight];
			for group in range(0,groups):
				groupRangeMin = boundaries[group][0];
				groupRangeMax = boundaries[group][1];
				if (pixelColor ==np.array([255,255,255])).all():
					continue;
				elif ( (pixelColor[channel] >= groupRangeMin) and (pixelColor[channel] < groupRangeMax) ):
					outputImages[group][height,weight] = pixelColor;

	for group in range(0,groups):
		cv.imwrite(outputDir+outputFormat%(group),outputImages[group]);
	return (outputDir+outputFormat),groups;

def labelingGrayImage(imageMatrix):
	labeledPic,regionsCnt = measure.label(imageMatrix,background=255,return_num=True,connectivity=2);
	props = measure.regionprops(labeledPic);
	print("regionsCnt is ",regionsCnt);
	return props;

def judgeRegions(regionItem):
	# centroid = regions[index].centroid;
	# bbox = regions[index].bbox;#(min_row, min_col, max_row, max_col)
	# max_x = bbox[3]-bbox[1];
	# max_y = bbox[2] - bbox[0];
	# size = max_x*max_y;
	# r = math.ceil(max(max_x,max_y)/2);
	# ratio = min(max_x,max_y)/r;
	return True;

def circleOnOriginalImage(originalImage,regionImage,regionImageColor=None): #regionImage should be gray
	regions = labelingGrayImage(regionImage);
	if regionImageColor:
		print(regions[20].perimeter);
		bbox = regions[20].bbox;#(min_row, min_col, max_row, max_col)
		max_x = bbox[3] - bbox[1];
		max_y = bbox[2] - bbox[0];
		region = regionImageColor[bbox[0]:bbox[2],bbox[1]:bbox[3]];
		cv.imwrite(currentDir_+"region20.bmp",region);

	for index in range(len(regions)):
		regionItem = regions[index];
		result = judgeRegions(regionItem);
		
		centroid = regionItem.centroid;
		bbox = regionItem.bbox;#(min_row, min_col, max_row, max_col)
		max_x = bbox[3]-bbox[1];
		max_y = bbox[2]-bbox[0];
		size = max_x*max_y;
		r = int(math.ceil(max(max_x,max_y)/2));
		# ratio = min(max_x,max_y)/r; 

		# print("r is %d "%(r));
		cv.circle(originalImage,(int(centroid[1]),int(centroid[0])), int(r), (0,0,255), 2);
		# font=cv.FONT_HERSHEY_SIMPLEX;
		font=cv.FONT_HERSHEY_COMPLEX_SMALL;
		cv.putText(originalImage,str(index),(int(centroid[1]),int(centroid[0])), font, 1.0,(0,255,0),thickness=2,lineType=8);

	return originalImage;

def main(argv):
	iniDir(argv);
	global currentDir_;
	global colorLevel_;
	global kernel;
	global channel;

	kernelSize = kernel[0];

	# reduce noise --> bg white  --> blur for channel  --> output files separated by color in channel --> use one to mark image
	# pick up Best Image for the Target Regions --> circle on the original  --> see the Results for marking

	# IMAGE B
	targetDir = getRelativeDir(["separateByColorLevel","blurByKer%dChannel%d"%(kernelSize,channel),"JF14_091_S8_HE"]);
	print(targetDir);
	if (not os.path.isdir(targetDir)):
		os.makedirs(targetDir);

	time0 = time.time();
	colorImage_1 = cv.imread(currentDir_+"JF14_091_S8_HE.bmp",COLORFULL);
	colorImage_1 = cv.GaussianBlur(colorImage_1,kernel,0);
	cv.imwrite(targetDir+"JF14_091_S8_HE_GaussianBlur.bmp",colorImage_1);
	colorImage_1 = reduceNoise(colorImage_1);
	cv.imwrite(targetDir+"JF14_091_S8_HE_noise.bmp",colorImage_1);
	maskImage_1 = getImageWithBlackBg(colorImage_1);


	ret,maskImage_2 = cv.threshold(colorImage_1[:,:,channel],0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU);
	cv.imwrite(targetDir+"JF14_091_S8_HE_mask3.bmp",maskImage_2);
	filterImageByBlackImage(colorImage_1,maskImage_1);
	newImage = np.zeros(colorImage_1.shape,dtype=np.uint8);
	newImage[::] = 255;
	
	for height in range(0,colorImage_1.shape[0]):
		for weight in range(0,colorImage_1.shape[1]):
			if (colorImage_1[height,weight]!=np.array([255,255,255])).all():
				newImage[height,weight,0] = np.uint8(255-(colorImage_1[height,weight,0]-colorImage_1[height,weight,1]))  #B
				newImage[height,weight,1] = np.uint8(255-(colorImage_1[height,weight,2]-colorImage_1[height,weight,1]))  #G
				newImage[height,weight,2] = np.uint8(255-(colorImage_1[height,weight,2]-colorImage_1[height,weight,0]));                                     #R
	cv.imwrite(targetDir+"JF14_091_S8_HE_minus.bmp",newImage);

	# fileFormat,outputGroups = separateColor(colorImage_1,"JF14_091_S8_HE_kernel%dChannel%d"%(kernelSize,channel)+"_group%d.bmp",targetDir);
	# print("fileFormat %s \ngroups is %d"%(fileFormat,outputGroups));
	# print("progress 1 over use time %d"%(time.time()-time0));   # 295

	# time1 = time.time();
	# group = 3;
	# bestRegions = cv.imread(targetDir+"JF14_091_S8_HE_kernel%dChannel%d_group%d.bmp"%(kernelSize,channel,group),GRAY);
	# # bestRegions_5_color = cv.imread(targetDir+"JF14_091_S8_HE_kernel15_group5.bmp",COLORFULL);
	# ret,bestRegions = cv.threshold(bestRegions,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU);

	# # # 对于分层结果图片，怎么判断哪些连通区域属于淋巴滤泡区域？哪些不是，依靠的鉴别特征是什么？
	# result = circleOnOriginalImage(cv.imread(currentDir_+"JF14_091_S8_HE.bmp",COLORFULL),bestRegions);
	# # # 多个结果，怎么选择最优的结果作为表示？
	# cv.imwrite(targetDir+"JF14_091_S8_HE_result_%d.bmp"%(group),result);
	# print("mark use time %d"%(time.time()-time1));

if __name__ == '__main__':
   main(sys.argv);

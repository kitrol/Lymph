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
from skimage import io,measure,color

currentDir_ = "";
colorLevel_ = "";
sysstr_ = "";
COLORFULL = 1;
GRAY = 0;
interval = 10.0;
channel = 2;
kernel = (9,9);

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

def minusAverage(image):
	global currentDir_;
	originalImage = cv.imread(currentDir_+"JF15_022_2_HE_gray.bmp",COLORFULL);
	grayImageWhole = cv.imread(currentDir_+"JF15_022_2_HE_gray.bmp",GRAY);
	for width in range(0,opening.shape[0]):
		for height in range(0,opening.shape[1]):
			if opening[width,height]==0:
				grayImageWhole[width,height]=255; 

def getImageWithWhiteBg(image):
	ret,regionImage = cv.threshold(image[:,:,2],0,255,cv.THRESH_BINARY+cv.THRESH_OTSU);
	cv.imwrite(currentDir_+"regionImage.bmp",regionImage);
	return regionImage;

def filterImageByBlackImage(originalImage,maskImage):
	# mask image should be black and white,the background of the originalImage should be white 
	# in maskImage and the tissue regions should be black.
	for height in range(0,maskImage.shape[0]):
		for width in range(0,maskImage.shape[1]):
			if maskImage[height,width]==255:
				originalImage[height,width,:]=255;

	return originalImage;

def separateColor(image,outputFormat,outputDir):
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

	redRange = maxInChannel-minInChannel;
	global interval;
	groups = int(math.ceil(redRange/interval));
	print(groups);
	for group in range(0,groups):
		newImage = np.zeros(image.shape,dtype=np.uint8);
		newImage[::] = 255;
		groupRangeMin = (group-1)*interval+minInChannel;
		groupRangeMax = group*interval+minInChannel;
		for height in range(0,image.shape[0]):
			for weight in range(0,image.shape[1]):
				if (image[height,weight]==np.array([255,255,255])).all():
					continue;
				elif ( (image[height,weight,channel] >= groupRangeMin) and (image[height,weight,channel] < groupRangeMax) and (max(image[height,weight]) - min(image[height,weight]) > 10) ):
					newImage[height,weight] = image[height,weight];
		cv.imwrite(outputDir+outputFormat%(group),newImage);
	fileFormat = outputDir+outputFormat;
	return fileFormat,groups;

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
		max_y = bbox[2] - bbox[0];
		size = max_x*max_y;
		r = math.ceil(max(max_x,max_y)/2);
		ratio = min(max_x,max_y)/r; 

		cv.circle(originalImage,(int(centroid[1]),int(centroid[0])), r, (0,0,255), 2);
		# font=cv.FONT_HERSHEY_SIMPLEX;
		font=cv.FONT_HERSHEY_COMPLEX_SMALL;
		cv.putText(originalImage,str(index),(int(centroid[1]),int(centroid[0])), font, 1.0,(0,255,0),thickness=2,lineType=8);

	return originalImage;

def main(argv):
	iniDir(argv);
	global currentDir_;
	global colorLevel_;
	global kernel;

	# blur -->  removeBg  -->  separatecolor  --> outPut
	# pick up Best Image for the Target Regions --> circle on the original  --> see the Results for marking

	# IMAGE A
	# colorImage_1 = cv.imread(currentDir_+"JF15_022_2_HE.bmp",COLORFULL);
	# maskImage_1 = getImageWithWhiteBg(colorImage_1);
	# colorImage_1[:,:,0] = cv.GaussianBlur(colorImage_1[:,:,0],kernel,0);
	# colorImage_1[:,:,1] = cv.GaussianBlur(colorImage_1[:,:,1],kernel,0);
	# colorImage_1[:,:,2] = cv.GaussianBlur(colorImage_1[:,:,2],kernel,0);
	# filterImageByBlackImage(colorImage_1,maskImage_1);
	# targetDir = getRelativeDir(["separateByColorLevel","blurOriImageByKer15","JF15_022_2_HE"]);
	# fileFormat,outputGroups = separateColor(colorImage_1,"JF15_022_2_HE_kernel15_group%d.bmp",targetDir);

	# targetDir = getRelativeDir(["separateByColorLevel","blurOriImageByKer15","JF15_022_2_HE"]);
	# # 如何选择最好的分层结果图片？
	# bestRegions_9 = cv.imread(targetDir+"JF15_022_2_HE_kernel15_group9.bmp",GRAY);
	# ret,bestRegions_9 = cv.threshold(bestRegions_9,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU);
	# cv.imwrite(currentDir_+"JF15_022_2_HE_bestRegions_9.bmp",bestRegions_9);
	# bestRegions_10 = cv.imread(targetDir+"JF15_022_2_HE_kernel15_group9.bmp",GRAY);
	# ret,bestRegions_10 = cv.threshold(bestRegions_10,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU);
	# cv.imwrite(currentDir_+"JF15_022_2_HE_bestRegions_10.bmp",bestRegions_10);
	# # 对于分层结果图片，怎么判断哪些连通区域属于淋巴滤泡区域？哪些不是，依靠的鉴别特征是什么？
	# result_9 = circleOnOriginalImage(cv.imread(currentDir_+"JF15_022_2_HE.bmp",COLORFULL),bestRegions_9);
	# result_10 = circleOnOriginalImage(cv.imread(currentDir_+"JF15_022_2_HE.bmp",COLORFULL),bestRegions_10);
	# # 多个结果，怎么选择最优的结果作为表示？
	# cv.imwrite(currentDir_+"JF15_022_2_HE_result_9.bmp",result_9);
	# cv.imwrite(currentDir_+"JF15_022_2_HE_result_10.bmp",result_10);


	# IMAGE B
	colorImage_1 = cv.imread(currentDir_+"JF14_091_S8_HE.bmp",COLORFULL);
	maskImage_1 = getImageWithWhiteBg(colorImage_1);
	# colorImage_1[:,:,0] = cv.GaussianBlur(colorImage_1[:,:,0],kernel,0);
	# colorImage_1[:,:,1] = cv.GaussianBlur(colorImage_1[:,:,1],kernel,0);
	colorImage_1[:,:,2] = cv.GaussianBlur(colorImage_1[:,:,2],kernel,0);
	filterImageByBlackImage(colorImage_1,maskImage_1);
	targetDir = getRelativeDir(["separateByColorLevel","blurOriImageByKer15","JF14_091_S8_HE"]);
	fileFormat,outputGroups = separateColor(colorImage_1,"JF14_091_S8_HE_kernel15_group%d.bmp",targetDir);
	print("fileFormat %s \ngroups is %d"%(fileFormat,outputGroups));

	# bestRegions_4 = cv.imread(targetDir+"JF14_091_S8_HE_kernel15_group4.bmp",GRAY);
	# # bestRegions_4_color = cv.imread(targetDir+"JF14_091_S8_HE_kernel15_group4.bmp",COLORFULL);
	# ret,bestRegions_4 = cv.threshold(bestRegions_4,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU);

	# bestRegions_5 = cv.imread(targetDir+"JF14_091_S8_HE_kernel15_group5.bmp",GRAY);
	# # bestRegions_5_color = cv.imread(targetDir+"JF14_091_S8_HE_kernel15_group5.bmp",COLORFULL);
	# ret,bestRegions_5 = cv.threshold(bestRegions_5,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU);
	
	# bestRegions_6 = cv.imread(targetDir+"JF14_091_S8_HE_kernel15_group6.bmp",GRAY);
	# # bestRegions_6_color = cv.imread(targetDir+"JF14_091_S8_HE_kernel15_group6.bmp",COLORFULL);
	# ret,bestRegions_6 = cv.threshold(bestRegions_6,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU);
	# # cv.imwrite(currentDir_+"JF14_091_S8_HE_bestRegions_5.bmp",bestRegions_5);
	# # cv.imwrite(currentDir_+"JF14_091_S8_HE_bestRegions_10.bmp",bestRegions_6);

	# # 对于分层结果图片，怎么判断哪些连通区域属于淋巴滤泡区域？哪些不是，依靠的鉴别特征是什么？
	# result_4 = circleOnOriginalImage(cv.imread(currentDir_+"JF14_091_S8_HE.bmp",COLORFULL),bestRegions_4);
	# result_5 = circleOnOriginalImage(cv.imread(currentDir_+"JF14_091_S8_HE.bmp",COLORFULL),bestRegions_5);
	# result_6 = circleOnOriginalImage(cv.imread(currentDir_+"JF14_091_S8_HE.bmp",COLORFULL),bestRegions_6);
	# # 多个结果，怎么选择最优的结果作为表示？
	# cv.imwrite(currentDir_+"JF14_091_S8_HE_result_4.bmp",result_4);
	# cv.imwrite(currentDir_+"JF14_091_S8_HE_result_5.bmp",result_5);
	# cv.imwrite(currentDir_+"JF14_091_S8_HE_result_6.bmp",result_6);

if __name__ == '__main__':
   main(sys.argv);

#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import openslide
import sys
import os
import numpy as np
import cv2 as cv

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
				newImage[height,weight,0] = np.uint8((colorImage_1[height,weight,0]-colorImage_1[height,weight,1]))  #B
				newImage[height,weight,1] = np.uint8((colorImage_1[height,weight,2]-colorImage_1[height,weight,1]))  #G
				newImage[height,weight,2] = colorImage_1[height,weight,2];                                               #R
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
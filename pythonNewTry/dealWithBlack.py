#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys
import cv2 as cv
import numpy as np

CommonKernelSize = (5,5);
DeleteSizeThreshold = 20;
SCALE = 1/10;
WHITE_1 = 255;
WHITE_3 = [255,255,255];
BLACK_1 = 0;
BLACK_3 = [0,0,0];
SuspiciousColor = 120;

def main(argv):
	if len(argv) < 2:
		usage="Usage: \n 1 Parameters are needed:\n image file. "
		print(usage);
		return False;
	####  Prepare Work  ####
	global CommonKernelSize,DeleteSizeThreshold,WHITE_1;
	global WHITE_3,BLACK_1,BLACK_3,SCALE,SuspiciousColor;
	fileName = argv[1]; 
	sourceImage = cv.imread(fileName);
	shape = sourceImage.shape;
	baseName = fileName.split('.')[0];
	maskImage = np.zeros((shape[0],shape[1]),dtype=np.uint8);
	maskImage[::] = WHITE_1;
	####  Prepare Work  ####

	####  Mark for BLACK  ####
	index = np.where(np.average(sourceImage,axis=2)<=100);
	sourceImage[index] = WHITE_3;
	maskImage[index] = BLACK_1;
	####  Mark for BLACK  ####

	# cv.imwrite(baseName+'_markblack.png',sourceImage);
	cv.imwrite(baseName+'_mask.png',maskImage);
	del sourceImage;

	####  Reduce the noise Round 1 ####
	# kernel = np.ones(CommonKernelSize,np.uint8);
	# dilation = cv.dilate(maskImage,kernel,iterations = 1);
	# erosion = cv.erode(dilation,kernel,iterations = 1);
	# cv.imwrite(baseName+'_dilation.png',dilation);
	# cv.imwrite(baseName+'_erosion.png',erosion);
	####  Reduce the noise Round 1 ####
	
	####  Reduce the noise Round 2 ####
	resize = cv.resize(maskImage, (int(shape[0]*SCALE), int(shape[1]*SCALE)), interpolation=cv.INTER_LANCZOS4);
	ret, resize = cv.threshold(resize,0,255,cv.THRESH_OTSU);
	ret, binimage = cv.threshold(resize,0,255,cv.THRESH_BINARY_INV);
	# del dilation;
	# del erosion;
	# cv.imwrite(baseName+'_INV_bin.png',binimage);
		# image for processing should be WHITE regions with BLACK background
		# nlabels: the numbers of all the regions;
		# labelsMatrix: same size with input image filled with the label for the regions
		# stats: profile for each region with deta like: [x0, y0, width, height, area]
		# centroids: the center for each region
	nlabels, labelsMatrix, stats, centroids = cv.connectedComponentsWithStats(binimage);
	# first item in stats seems to be the background profile
	for label in range(1,nlabels):
		if stats[label][4] <= DeleteSizeThreshold:
			index = np.where(labelsMatrix==label);
			binimage[index] = BLACK_1;
			resize[index] = WHITE_1;
		# if stats[label][4] >= stats[label][2]*stats[label][3]/4:
		# 	subImage = resize[stats[label][0]:stats[label][0]+stats[label][2],stats[label][1]:stats[label][1]+stats[label][3]];
		# 	cv.imwrite(baseName+'_bin_%d.png'%(label),subImage);
	# cv.imwrite(baseName+'_bin_1.png',binimage);
	# cv.imwrite(baseName+'_bin_2.png',resize);

	nlabels, labelsMatrix, stats, centroids = cv.connectedComponentsWithStats(binimage);
	suspiciousLabels = [];
	for label in range(1,nlabels):
		if (stats[label][4] >= stats[label][2]*stats[label][3]/3) or (stats[label][4] <= DeleteSizeThreshold*3):
			# solid: if the area size is bigger than width*height/3 mark it as suspicious
			# small region within the size of DeleteSizeThreshold*2 wait for second check
			index = np.where(labelsMatrix==label);
			resize[index] = SuspiciousColor;
			if label not in suspiciousLabels:
				suspiciousLabels.append(label);
	cv.imwrite(baseName+'_suspicious.png',resize);
	# for a suspicious region, find a bigger near region but not suspicious, if near enough, remove from suspicious labels
	noSuspicious = [];
	# print(suspiciousLabels);
	def makeInRange(rangetuple,num):
		if num < rangetuple[0]:
			return rangetuple[0];l
		elif num >= rangetuple[1]:
			return rangetuple[1]-1;
		else:
			return num;
	for label in suspiciousLabels:
		targetStats = stats[label];
		areaSize = targetStats[4]; 
		center = (targetStats[0]+int(targetStats[2]/2),targetStats[1]+int(targetStats[3]/2));
		radius = int(max((targetStats[2],targetStats[3]))/2+10);
		# cv.circle(resize,center, radius, 0, 1);
		isFind = False;
		index = np.where(labelsMatrix==label);
		for x in range(-radius,radius):
			for y in range(-radius,radius):
				# try to find a nearest unsuspicious region
				targe_x = makeInRange((0,resize.shape[0]),center[0]+x);
				targe_y = makeInRange((0,resize.shape[1]),center[1]+y);
				# otherLabel = labelsMatrix[targe_x,targe_y];
				otherLabel = labelsMatrix[targe_y,targe_x];
				if (otherLabel != 0) and (otherLabel != label) and (otherLabel not in suspiciousLabels) and (areaSize <= stats[otherLabel][4]/2):
					# print("areaSize is %d otherLabel %d otherSize %d"%(areaSize,otherLabel,stats[otherLabel][4]));
					resize[index] = BLACK_1;
					binimage[index] = WHITE_1;
					if label not in noSuspicious:
						noSuspicious.append(label);
					isFind = True;
					break;
			if isFind:
				break;
		if not isFind:
			resize[index] = WHITE_1;
			binimage[index] = BLACK_1;

	# print(noSuspicious);
	cv.imwrite(baseName+'_clear.png',resize);
	for label in noSuspicious:
		suspiciousLabels.remove(label);
	####  Reduce the noise Round 2 ####



if __name__ == '__main__':
    main(sys.argv)
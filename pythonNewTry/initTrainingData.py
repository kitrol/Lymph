#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys
import os
import cv2 as cv
import numpy as np
VESSEL = [1,1,1];
ERYTHROCYTE = [0,255,255];
NEGATIVE = [0,0,255];
RangeType=["Nine-Box",
			"Sixteen-Box",
			"Five-Sixteen-Box",
			"Five-Sixteen-Box",];
def getDataNineBox(sourceImg,y,x):
	shape = sourceImg.shape;
	if (y-1)<0 or (y+1)>shape[0]-1 or (x-1)<0 or (x+1)>shape[1]-1:
		return False,None;
	else:
		return True,sourceImg[y-1:y+2,x-1:x+2];

def getDataTwentyfiveBox(sourceImg,y,x):
	shape = sourceImg.shape;
	if (y-2)<0 or (y+2)>shape[0]-1 or (x-2)<0 or (x+2)>shape[1]-1:
		return False,None;
	else:
		return True,sourceImg[y-2:y+3,x-2:x+3].reshape(-1);

def getDataFortynineBox(sourceImg,y,x):
	shape = sourceImg.shape;
	if (y-3)<0 or (y+3)>shape[0]-1 or (x-3)<0 or (x+3)>shape[1]-1:
		return False,None;
	else:
		return True,sourceImg[y-3:y+4,x-3:x+4].reshape(-1);
def main(argv):
	if len(argv) < 2:
		usage="Usage: \n 1 Parameters are needed:\n image file. "
		print(usage);
		return False;
	fileName = argv[1];
	baseName = fileName.split('.')[0];
	markedImage = cv.imread(fileName);
	originalName = baseName.replace("_train","")+".png";
	originalFile = cv.imread(originalName);
	vesselData = [];
	negativeData = [];
	erythrocyteData = [];
	# vesselImg = np.zeros(markedImage.shape,dtype=np.uint8);
	# erythrocyteImg = np.zeros(markedImage.shape,dtype=np.uint8);
	# negativeImg = np.zeros(markedImage.shape,dtype=np.uint8);
	# vesselImg[::]=erythrocyteImg[::]=negativeImg[::]=255;
	for y in range(0,markedImage.shape[0]):
		for x in range(0,markedImage.shape[1]):
			# isGet,data = getDataTwentyfiveBox(originalFile,y,x);
			isGet,data = getDataFortynineBox(originalFile,y,x);
			if isGet == False:
				continue;
			color = markedImage[y,x];
			# originalColor = originalFile[y,x];
			if (color == np.array(VESSEL)).all():
				vesselData.append(data);	
			elif (color == np.array(ERYTHROCYTE)).all():
				erythrocyteData.append(data);
			elif (color == np.array(NEGATIVE)).all():
				negativeData.append(data);

	print(len(vesselData));
	print(len(negativeData));
	print(len(erythrocyteData));
	# cv.imwrite(baseName+"vesselImg.png",vesselImg);
	trainCsv = baseName+"train.csv";
	if os.path.isfile(trainCsv):	
		os.remove(trainCsv);
	file = open(trainCsv, "w+");
	for index in range(0,len(vesselData)):
		string = '1,';
		for item in vesselData[index]:
			string+=str(item)+",";
		string+="1\n";
		file.write(string);

	for index in range(0,len(negativeData)):
		string = '1,';
		for item in negativeData[index]:
			string+=str(item)+",";
		string+="0\n";
		file.write(string);

	for index in range(0,len(erythrocyteData)):
		string = '1,';
		for item in erythrocyteData[index]:
			string+=str(item)+",";
		string+="0\n";
		file.write(string);
	file.close();

if __name__ == '__main__':
    main(sys.argv)
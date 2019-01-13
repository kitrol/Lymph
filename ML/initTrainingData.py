#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys,os,math 
import cv2 as cv
import numpy as np
VESSEL = [1,1,1];
ERYTHROCYTE = [0,255,0];
NEGATIVE = [0,0,255];
RangeType = 81; #25,49,81,121
# ["Nine-Box",
# 			"Sixteen-Box",
# 			"Five-Sixteen-Box",
# 			"Five-Sixteen-Box",];
def getDataSquare(sourceImg,y,x):
	global RangeType;
	offset = int((math.sqrt(RangeType)-1)/2);
	shape = sourceImg.shape;
	if (y-offset)<0 or (y+offset)>shape[0]-1 or (x-offset)<0 or (x+offset)>shape[1]-1:
		return False,None;
	else:
		return True,sourceImg[y-offset:y+offset+1,x-offset:x+offset+1].reshape(-1);

def readDataFromFile(trainImageName):
	global VESSEL,ERYTHROCYTE,NEGATIVE,RangeType;
	baseName = trainImageName.split('.')[0];
	markedImage = cv.imread(trainImageName);
	originalName = baseName.replace("_train","")+".png";
	originalFile = cv.imread(originalName);
	vesselData = [];
	negativeData = [];
	erythrocyteData = [];
	for y in range(0,markedImage.shape[0]):
		for x in range(0,markedImage.shape[1]):
			isGet,data = getDataSquare(originalFile,y,x);
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
	# print(len(vesselData));
	# print(len(negativeData));
	# print(len(erythrocyteData));
	return vesselData,negativeData,erythrocyteData;
def writeToFile(fileHandle,data,dataType):
	for index in range(0,len(data)):
		string = '1,'; # add bias data
		for item in data[index]:
			string+=str(item)+",";
		string+="%d\n"%(dataType);
		fileHandle.write(string);
	fileHandle.flush();
	
def main(argv):
	if len(argv) < 2:
		usage="Usage: \n 1 Parameters are needed:\n Trian File Folder with Original Images. "
		print(usage);
		return False;
	global RangeType;
	trainFolder = argv[1];
	vessel = [];
	negative = [];
	erythrocyte = [];
	trainCsv = os.path.join(trainFolder,"train_%d.csv"%(RangeType));
	if os.path.isfile(trainCsv):	
		os.remove(trainCsv);
	file = open(trainCsv, "w+");
	if os.path.exists(trainFolder):
		for fileName in os.listdir(trainFolder):
			trianFileName = os.path.join(trainFolder,fileName);
			if os.path.isfile(trianFileName) and trianFileName.find("_train") > 0 and os.path.isfile(trianFileName.replace("_train","")):
				print("Processing: "+fileName+" ");
				vessel_,negative_,erythrocyte_ = readDataFromFile(trianFileName);
				# originalFile = trianFileName.replace("_train","");
				# print(originalFile);
				vessel.extend(vessel_);
				negative.extend(negative_);
				erythrocyte.extend(erythrocyte_);
				writeToFile(file,vessel_,dataType=1);
				writeToFile(file,negative_,dataType=0);
				writeToFile(file,erythrocyte_,dataType=2);
	file.close();
	print(len(vessel));
	print(len(negative));
	print(len(erythrocyte));

if __name__ == '__main__':
    main(sys.argv)
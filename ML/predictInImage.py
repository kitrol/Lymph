#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys,os,re,math,random,time
import cv2 as cv
import numpy as np
from sklearn.neural_network import MLPClassifier
import pickle
import sklearn.externals as sk_externals

RangeType = 0; # will be changed in main func
DoneProcessCounter = 0;

def predictWithRange(packedImage,detectRange,rangeType,processIndex,modelFileName,counter,posArray,processLock):
	# print("processIndex  %d "%(processIndex));
	# print(packedImage[100,100]);
	clf = None;
	with open(modelFileName, 'rb') as file:
		clf = pickle.load(file);
	start_Y = detectRange['start_Y'];
	end_Y = detectRange['end_Y'];
	start_X = detectRange['start_X'];
	end_X = detectRange['end_X'];
	shape = packedImage.shape;
	stepSize = int(math.ceil(rangeType-1));
	for y in range(start_Y,end_Y,stepSize):
		for x in range(start_X,end_X,stepSize):
			if (y+rangeType)<=shape[0] and (x+rangeType)<=shape[1]:
				temp = packedImage[y:y+rangeType,x:x+rangeType].reshape(-1);
				targetData = np.append([1], temp).reshape(1,-1);
				y_pred = clf.predict(targetData.reshape(1,-1));
				# if (y-start_Y)>0 and (y-start_Y)%1000 == 0:
				# 	print("ID: %d current process row %d"%(processIndex,y));
				if y_pred != 0:
					processLock.acquire();
					pos = [y,x,y_pred];
					posArray.put(pos);
					processLock.release();

	processLock.acquire();
	time.sleep(0.5);
	counter.value += 1;
	print("Process %d is Finished."%(processIndex));
	processLock.release();

def onGetItemPos(sourceImage,data):
	if data[2] == 1:
		sourceImage[data[0],data[1]]=[0,255,0];
	elif data[2] == 2:
		sourceImage[data[0],data[1]]=[0,0,255];
	

def checkImagePiece(model,modelFileName,imageName):
	imageItem = cv.imread(imageName);
	shape = imageItem.shape;
	import multiprocessing
	global RangeType;
	processCnt = multiprocessing.cpu_count()-1;
	lock = multiprocessing.Lock();
	positions = multiprocessing.Queue();
	processCounter = multiprocessing.Value("i",0);
	start_X = 0;
	start_Y = 0;
	end_X = shape[1];
	end_Y = shape[0];
	detectRange = {'start_X':0,'start_Y':0,'end_X':shape[1],'end_Y':shape[0]};
	y_offset = int(math.floor( (shape[0]-RangeType)/processCnt));
	process = [];
	for index in range(0,processCnt):
		detectRange['start_Y'] = index*y_offset;
		if (index+1)==processCnt:
			detectRange['end_Y'] = shape[0];
		else:
			detectRange['end_Y'] = (index+1)*y_offset;
		p = multiprocessing.Process(target=predictWithRange, args=(imageItem,detectRange,RangeType,index,modelFileName,processCounter,positions,lock));
		process.append(p);
		p.start();

	IsFind = False;
	while processCounter.value < processCnt:
		if not positions.empty():
			IsFind = True;
			data = positions.get();
			# print('Predicet Vessel Pos '+str(pos));
			onGetItemPos(imageItem,data);
	print("%s Process is Finished."%(imageName));
	for x in process:
		if x.is_alive():
			x.terminate();
		# print('pid %d %s'%(x.pid,str(x.is_alive())));
	if IsFind:
		fileName = os.path.basename(imageName);
		cv.imwrite(os.path.join(r'C:\Users\kitrol\Desktop\MachineLearning\TestResult',fileName),imageItem);


def main(argv):
	if len(argv) < 3:
		usage="Usage: \n 2 Parameters are needed:\n 1.Trained Model File Path 2.HE fils folder full path "
		print(usage);
		return False;
	modelFileName = argv[1];
	clf = None;
	global RangeType;
	with open(modelFileName, 'rb') as model:
		clf = pickle.load(model);
		baseName = modelFileName.split('.')[0];
		RangeType = int((baseName.split('\\')[-1]).split('_')[-1]);
	if clf == None:
		print("Read Model Failed!!");
		return False;

	# testImageName = argv[2];
	folderOrFile = argv[2];
	if os.path.isfile(folderOrFile): # parameter2 is a image file
		checkImagePiece(clf,modelFileName,os.path.join(folderOrFile,folderOrFile));
	else: # parameter2 is a folder of image
		if os.path.exists(folderOrFile):
			for fileName in os.listdir(folderOrFile):
				if fileName.find(".png") >= 0: # not the desc.txt file, image file
					checkImagePiece(clf,modelFileName,os.path.join(folderOrFile,fileName));				
	print("done");

if __name__ == '__main__':
    main(sys.argv)
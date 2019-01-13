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
ImageOffset = 20;

def predictWithRange(packedImage,detectRange,rangeOffset,processIndex,modelFileName,counter,posArray,processLock):
	# print("processIndex  %d "%(processIndex));
	# print(packedImage[100,100]);
	clf = None;
	with open(modelFileName, 'rb') as file:
		clf = pickle.load(file);
	start_Y = detectRange['start_Y'];
	end_Y = detectRange['end_Y'];
	start_X = detectRange['start_X'];
	end_X = detectRange['end_X'];

	for y in range(start_Y,end_Y):
		for x in range(start_X,end_X):
			temp = packedImage[(y-rangeOffset):(y+rangeOffset+1),(x-rangeOffset):(x+rangeOffset+1)];
			targetData = np.append([1], packedImage[(y-rangeOffset):(y+rangeOffset+1),(x-rangeOffset):(x+rangeOffset+1)].reshape(-1) );
			y_pred = clf.predict(targetData.reshape(1,-1));
			if (y-start_Y)>0 and (y-start_Y)%1000 == 0:
				print("ID: %d current process row %d"%(processIndex,y));
			if y_pred != 0:
				processLock.acquire();
				pos = [y,x,y_pred];
				posArray.put(pos);
				processLock.release();

	processLock.acquire();
	time.sleep(0.5);
	counter.value += 1;
	processLock.release();

def onGetItemPos(sourceImage,data):
	if data[2] == 1:
		sourceImage[data[0],data[1]]=[0,0,255];
	elif data[2] == 2:
		sourceImage[data[0],data[1]]=[0,255,0];
	

def checkImagePiece(model,modelFileName,imageName):
	imageItem = cv.imread(imageName);
	shape = imageItem.shape;
	import multiprocessing
	global RangeType;
	rangeOffset = int((math.sqrt(RangeType)-1)/2);
	processCnt = multiprocessing.cpu_count()-1;
	lock = multiprocessing.Lock();
	positions = multiprocessing.Queue();
	processCounter = multiprocessing.Value("i",0);
	start_X = rangeOffset;
	start_Y = rangeOffset;
	end_X = shape[1]-rangeOffset;
	end_Y = shape[0]-rangeOffset;
	detectRange = {'start_X':start_X,'start_Y':start_Y,'end_X':end_X,'end_Y':end_Y};
	y_offset = int(math.floor( (shape[0]-rangeOffset)/processCnt));
	process = [];
	for index in range(0,processCnt):
		detectRange['start_Y'] = index*y_offset+rangeOffset;
		if (index+1)==processCnt:
			detectRange['end_Y'] = shape[0]-rangeOffset;
		else:
			detectRange['end_Y'] = (index+1)*y_offset+rangeOffset;
		p = multiprocessing.Process(target=predictWithRange, args=(imageItem,detectRange,rangeOffset,index,modelFileName,processCounter,positions,lock));
		process.append(p);
		p.start();

	IsFind = False;
	while processCounter.value < processCnt:
		if not positions.empty():
			IsFind = True;
			data = positions.get();
			# print('Predicet Vessel Pos '+str(pos));
			onGetItemPos(imageItem,data);
	print("Process Finish");
	for x in process:
		if x.is_alive():
			x.terminate();
		# print('pid %d %s'%(x.pid,str(x.is_alive())));
	if IsFind:
		fileName = os.path.basename(imageName);
		cv.imwrite(os.path.join(r'C:\Users\kitrol\Desktop\MachineLearning\TestResult',fileName),imageItem);


def main(argv):
	if len(argv) < 2:
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

	testImageName = argv[2];
	# print("get filename:",os.path.basename(testImageName));
	checkImagePiece(clf,modelFileName,testImageName);
	print("done");

if __name__ == '__main__':
    main(sys.argv)
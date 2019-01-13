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
	global ImageOffset;
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
				print("ID: %d current process row %d"%(processIndex,y-ImageOffset));
			if y_pred == 1:
				processLock.acquire();
				pos = [y-ImageOffset,x-ImageOffset];
				posArray.put(pos);
				processLock.release();

	processLock.acquire();
	time.sleep(0.5);
	counter.value += 1;
	processLock.release();

def onGetVesselPos(sourceImage,y,x):
	sourceImage[y,x]=[0,0,255];

def checkImagePiece(folderName,imageName,totalRows,totalColumns,model,modelFileName):
	matchObj = re.match(r'.*_c(.*)_lv_(.*)_row_(.*)_clo_(.*).png',imageName,re.I);
	if matchObj:
		currentRow = int(matchObj.group(3));
		currentCol = int(matchObj.group(4));
		# print("currentRow %d currentCol %d "%(currentRow,currentCol));
		# print(os.path.join(folderName,imageName));
		pieceImage = cv.imread(os.path.join(folderName,imageName));
		shape = pieceImage.shape;
		global ImageOffset;
		offset = ImageOffset;
		start_X = offset;
		start_Y = offset;
		end_X = shape[1]-1;
		end_Y = shape[0]-1;
		fileNameMap = {};
		fileNameMap['left_up'] = imageName.replace('row_%d'%(currentRow),'row_%d'%(currentRow-1)).replace('clo_%d'%(currentCol),'clo_%d'%(currentCol-1));
		fileNameMap['up'] = imageName.replace('row_%d'%(currentRow),'row_%d'%(currentRow-1));
		fileNameMap['right_up'] = imageName.replace('row_%d'%(currentRow),'row_%d'%(currentRow-1)).replace('clo_%d'%(currentCol),'clo_%d'%(currentCol+1));
		fileNameMap['left'] = imageName.replace('clo_%d'%(currentCol),'clo_%d'%(currentCol-1));
		fileNameMap['right'] = imageName.replace('clo_%d'%(currentCol),'clo_%d'%(currentCol+1));
		fileNameMap['left_down'] = imageName.replace('row_%d'%(currentRow),'row_%d'%(currentRow+1)).replace('clo_%d'%(currentCol),'clo_%d'%(currentCol-1));
		fileNameMap['down'] = imageName.replace('row_%d'%(currentRow),'row_%d'%(currentRow+1));
		fileNameMap['right_down'] = imageName.replace('row_%d'%(currentRow),'row_%d'%(currentRow+1)).replace('clo_%d'%(currentCol),'clo_%d'%(currentCol+1));
		# print(fileNameMap.keys());
		if currentCol == 0:
			for key in fileNameMap.keys():
				if key.find('left') >=0:
					fileNameMap[key] = '';
		if currentCol == totalColumns-1:
			for key in fileNameMap.keys():
				if key.find('right') >=0:
					fileNameMap[key] = '';
		if currentRow == 0:
			for key in fileNameMap.keys():
				if key.find('up') >=0:
					fileNameMap[key] = '';
		if currentRow == totalRows-1:
			for key in fileNameMap.keys():
				if key.find('down') >=0:
					fileNameMap[key] = '';
		newImage = np.zeros((pieceImage.shape[0]+offset*2,pieceImage.shape[1]+offset*2,pieceImage.shape[2]),dtype=np.uint8);
		newImage[::] = 255;
		newImage[offset:-offset,offset:-offset,:] = pieceImage[:,:,:];
		for (key,value) in fileNameMap.items():
			# print(key+"  *"+value+"*");
			if value != '':
				# left_up    up   right_up
				# left    current   right
				# left_down down right_down
				packImage = cv.imread(os.path.join(folderName,value));
				if key == 'left_up':
					newImage[:offset,:offset,:] = packImage[-offset:,-offset:,:];
				if  key == 'up':
					newImage[:offset,offset:-offset,:] = packImage[-offset:,:,:];
				if  key == 'right_up':
					newImage[:offset,-offset:,:] = packImage[:offset,:offset,:];
				if  key == 'left':
					newImage[offset:-offset,:offset,:] = packImage[:,-offset:,:];
				if  key == 'right':
					newImage[offset:-offset,-offset:,:] = packImage[:,:offset,:];
				if  key == 'left_down':
					newImage[-offset:,:offset,:] = packImage[-offset:,-offset:,:];
				if  key == 'down':
					newImage[-offset:,offset:-offset,:] = packImage[:offset,:,:];
				if  key == 'right_down':
					newImage[-offset:,-offset:,:] = packImage[:offset,:offset,:];
		# cv.imwrite(os.path.join(r'C:\Users\kitrol\Desktop\out',imageName),newImage);
		#mark in new image
		import multiprocessing
		processCnt = multiprocessing.cpu_count()-1;
		lock = multiprocessing.Lock();
		positions = multiprocessing.Queue();
		processCounter = multiprocessing.Value("i",0);
		detectRange = {'start_X':start_X,'start_Y':start_Y,'end_X':end_X,'end_Y':end_Y};
		# newImagecopy = sharedmem.empty(newImage.shape, newImage.dtype);
		# newImagecopy[:] = newImage.copy();
		y_offset = int(math.floor(shape[0]/processCnt));
		global RangeType;
		rangeOffset = int((math.sqrt(RangeType)-1)/2);
		for index in range(0,processCnt):
			detectRange['start_Y'] = index*y_offset+offset;
			if (index+1)==processCnt:
				detectRange['end_Y'] = shape[0]+offset;
			else:
				detectRange['end_Y'] = (index+1)*y_offset+offset;
			p = multiprocessing.Process(target=predictWithRange, args=(newImage,detectRange,rangeOffset,index,modelFileName,processCounter,positions,lock));
			p.start();
			# p.join();

		IsFind = False;
		while processCounter.value < processCnt:
			if not positions.empty():
				IsFind = True;
				pos = positions.get();
				print('Predicet Vessel Pos '+str(pos));
				onGetVesselPos(pieceImage,pos[0],pos[1]);
		print("Process Finish");
		if IsFind:
			cv.imwrite(os.path.join(r'C:\Users\kitrol\Desktop\MachineLearning\TestResult',imageName),pieceImage);
		# while processCounter.value <= processCnt:
			
		# print('35345345345');
		# print(positions.qsize());
		# # print(positions.get());
		# print("process done!");
		# global RangeType;
		# rangeOffset = int((math.sqrt(RangeType)-1)/2);
		# for y in range(start_Y,end_Y):
		# 	if (y-start_Y)%1000==0:
		# 		print("current process row %d"%(y-start_Y));
		# 	for x in range(start_X,end_X):
		# 		targetData = np.append([1],newImage[(y-rangeOffset):(y+rangeOffset+1),(x-rangeOffset):(x+rangeOffset+1)].reshape(-1));
		# 		# print(targetData.shape);
		# 		# print(targetData);
		# 		y_pred = model.predict(targetData.reshape(1,-1));
				
		# 		if y_pred == 1:
		# 			pieceImage[y-start_Y,x-start_X] = [0,0,255];
		# 		else:
					# print("123123");
					# pieceImage[y-start_Y,x-start_X] = [255,255,255];
				# if y-start_Y>300:
				# 	cv.imwrite(os.path.join(r'C:\Users\kitrol\Desktop\MachineLearning\TestResult',imageName),pieceImage[:3000,:,:]);
				# 	return;
				# return;
		# sava the marked image
		# cv.imwrite(os.path.join(r'C:\Users\kitrol\Desktop\MachineLearning\TestResult',imageName),pieceImage);
	else:
		print("No Match!!");


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

	imageFolder = argv[2];
	txtFileName = os.path.join(imageFolder,"des.txt");
	descDict = {};
	if os.path.isfile(txtFileName):
		descFile = open(txtFileName, "r");
		descString = descFile.read();
		descList = descString.split("\n");
		for line in descList:
			if len(line)>2:
				item = line.split(":");
				descDict[item[0]] = int(item[1]);
	else:
		print("Can Not Open desc.txt File!");
		return False;
	# {'width': 72000, 'height': 33669, 'pieceSize': 10000, 'rows': 4, 'columns': 8}
	print(descDict);

	if os.path.exists(imageFolder):
		for fileName in os.listdir(imageFolder):
			if fileName.find(".txt") < 0: # not the desc.txt file, image file
				checkImagePiece(imageFolder,fileName,descDict['rows'],descDict['columns'],clf,modelFileName);
				return;


if __name__ == '__main__':
    main(sys.argv)
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys,os,re,math
import cv2 as cv
import numpy as np
from sklearn.neural_network import MLPClassifier

RangeType = 9;


def checkImagePiece(folderName,imageName,totalRows,totalColumns):
	matchObj = re.match(r'.*_c(.*)_lv_(.*)_row_(.*)_clo_(.*).png',imageName,re.I);
	if matchObj:
		currentRow = int(matchObj.group(3));
		currentCol = int(matchObj.group(4));
		print("currentRow %d currentCol %d "%(currentRow,currentCol));
		image = cv.imread(os.join(folderName,imageName));
		shape = iamge.shape;
		global RangeType;
		offset = (math.sqrt(RangeType)-1);
		start_X += 0;
		start_y += 0;
		end_X = shape[1]-1;
		end_Y = shape[0]-1;
		left_image = None;
		right_image = None;
		up_image = None;
		down_image = None;
		if currentCol == 0:
			start_X += offset;
		if currentCol == totalColumns-1:
			end_X -= offset; 
		if currentRow == 0:
			start_y += offset;
		if currentRow == totalRows-1:
			end_Y -= offset;
	else:
		print("No Match!!");


def main(argv):
	if len(argv) < 2:
		usage="Usage: \n 1 Parameters are needed:\n HE fils folder full path "
		print(usage);
		return False;
	imageFolder = argv[1];
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
				checkImagePiece(imageFolder,fileName,descDict['rows'],descDict['columns']);

if __name__ == '__main__':
    main(sys.argv)
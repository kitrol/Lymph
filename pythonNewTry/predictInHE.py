#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys
import os
import cv2 as cv
import re
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn import svm
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split

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
	print(descDict);		

	

	
	# testStr = r'2017SM01680_6_HE_c3_lv_0_row_15_clo_205.png';
	# # '(.*) are (.*?) .*'
	# # matchObj = re.match(r'_c(.*)_lv_(.*)_row_(.*)_clo_(.*).*',testStr,re.I);
	# matchObj = re.match(r'.*_c(.*)_lv_(.*)_row_(.*)_clo_(.*).png',testStr,re.I);
	# if matchObj:
	# 	descDict['channel'] = int(matchObj.group(1));
	# 	descDict['level'] = int(matchObj.group(2));
	# 	descDict['row_index'] = int(matchObj.group(3));
	# 	descDict['column_index'] = int(matchObj.group(4));
	# 	# print(matchObj.group(1));
	# 	# print(matchObj.group(2));
	# 	# print(matchObj.group(3));
	# 	# print(matchObj.group(4));
	# 	print(descDict);
	# else:
	# 	print("No Match");
	if os.path.exists(imageFolder):
		for fileName in os.listdir(imageFolder):
			if fileName.find(".txt") < 0: # not the desc.txt file, image file
				print(fileName);
				

if __name__ == '__main__':
    main(sys.argv)
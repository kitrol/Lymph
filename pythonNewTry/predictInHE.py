#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys
import os
import cv2 as cv
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
	txtFileName = "des.txt";
	descDict = {};
	if os.path.exists(imageFolder):
		for fileName in os.listdir(imageFolder):
			if fileName.find(".txt") > 0:
				txtFileName = os.path.join(imageFolder,fileName);
				file = open(txtFileName, "r");
				descString = file.read();
				descList = descString.split("\n");
				for line in descList:
					if len(line)>2:
						item = line.split(":");
						descDict[item[0]] = int(item[1]);
				print(descDict);
			else:
				print(fileName);

if __name__ == '__main__':
    main(sys.argv)
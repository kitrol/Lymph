#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys,os,math 
import cv2 as cv
import numpy as np
VESSEL = [2,2,2];
ERYTHROCYTE = [0,255,0];
NEGATIVE = [0,0,255];
RangeType = 9; #5,7,9,11,13,15,21
def checkMarkedData(folderName):
	global VESSEL,ERYTHROCYTE,NEGATIVE;
	if os.path.exists(folderName):
		for f in os.listdir(folderName):
			if f.find(r'.png') and f.find(r'_train') >= 0:
				sourceName = f.replace(r'_train','');
				print(sourceName);
				sourceImage = cv.imread(os.path.join(folderName,sourceName));
				markImage = cv.imread(os.path.join(folderName,f));
				outImage = np.zeros(sourceImage.shape,dtype=np.uint8);
				outImage[::] = 255;
				for y in range(0,sourceImage.shape[0]):
					for x in range(0,sourceImage.shape[1]):
						if (markImage[y,x]<=np.array(VESSEL)).all():
							outImage[y,x] = sourceImage[y,x];
						elif (markImage[y,x]==np.array(ERYTHROCYTE)).all():
							outImage[y,x] = sourceImage[y,x];
						elif (markImage[y,x]==np.array(NEGATIVE)).all():
							outImage[y,x] = sourceImage[y,x];
				cv.imwrite(os.path.join(folderName,'out'+f),outImage);
				
def main(argv):
	checkMarkedData(argv[1]);
	# changeNamesInFolder(argv[1]);


if __name__ == '__main__':
    main(sys.argv)
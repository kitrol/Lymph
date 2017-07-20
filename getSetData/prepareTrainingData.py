#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import cv2 as cv
import numpy as np
import sys
import os
import subprocess
import platform



worktDir_ = '';
TrainFolder = '\\..\\..\\train_data';
sysstr = platform.system();
print(sysstr);
if sysstr == "Windows":
	pass;
else:
	TrainFolder = '/../../train_data';

def readImage(fileName):
	img = cv.imread(fileName);
	return img;

def main(argv):
	global worktDir_;
	worktDir_ = os.path.dirname(argv[0]);
	print(worktDir_);
	global TrainFolder;
	TrainFolder = worktDir_+TrainFolder;
	os.chdir(TrainFolder);



	oriImg = readImage('JF14_091_S8_HE.bmp');
	correctImg = readImage('JF14_091_S8_HE_correct.bmp');
	# regionsImage = np.zeros();
	print(correctImg.shape);
	print(correctImg.size);
	print(correctImg.dtype);


	print(oriImg.shape);
	print(oriImg.size);
	print(oriImg.dtype);
	regionsImage = np.zeros(correctImg.shape,dtype=np.uint8);

	sumNum_R = 0.0;
	sumNum_G = 0.0;
	sumNum_B = 0.0;

	sumNum_R += oriImg[0,0,0];
	sumNum_G += oriImg[0,0,1];
	sumNum_B += oriImg[0,0,3];

	for width in range(0,oriImg.shape[0]):
		for height in range(0,oriImg.shape[1]):
			# print("pixel data is ",oriImg[width,height]);
			if (correctImg[width,height]==np.array([0,0,0])).all():
				print(correctImg[width,height]);
				regionsImage[width,height] = oriImg[width,height];
				pass;
			elif (oriImg[width,height]==correctImg[width,height]).all():
				sumNum
				
				pass;
			elif (correctImg[width,height]==np.array([0,0,0])).all():
				pass;



	cv.namedWindow('correctImg',cv.WINDOW_NORMAL);
	cv.imshow('correctImg',correctImg);
	# os.getcwd();
	# listfile=os.listdir(os.getcwd());
	# print(listfile);
	cv.waitKey(10000);
	cv.destroyAllWindows();


if __name__ == '__main__':
   main(sys.argv)
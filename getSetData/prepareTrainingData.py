#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import cv2 as cv
import numpy as np
import sys
import os
import subprocess


worktDir_ = '';
TrainFolder = '\\..\\..\\train_data';
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
	regionsImage = np.zeros(correctImg.shape,np.int8);

	for x in range(1,10):
		pass


	cv.namedWindow('correctImg',cv.WINDOW_NORMAL);
	cv.imshow('correctImg',correctImg);
	# os.getcwd();
	# listfile=os.listdir(os.getcwd());
	# print(listfile);
	cv.waitKey(10000);
	cv.destroyAllWindows();


if __name__ == '__main__':
    main(sys.argv)
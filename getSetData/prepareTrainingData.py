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
TextFolder = '\\..\\..\\markedRegionsText\\';
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
	pixels = 0;
	markedColors = [];

	for width in range(0,oriImg.shape[0]):
		for height in range(0,oriImg.shape[1]):
			pixels += 1;
			sumNum_R = oriImg[width,height,0];
			sumNum_G = oriImg[width,height,1];
			sumNum_B = oriImg[width,height,2];
			if (pixels==2):
				sumNum_R = sumNum_R/2;
				sumNum_G = sumNum_G/2;
				sumNum_B = sumNum_B/2;
				pass;
			elif pixels>2:
				sumNum_R = sumNum_R/2;
				sumNum_G = sumNum_G/2;
				sumNum_B = sumNum_B/2;
				pass;

			if (correctImg[width,height]==np.array([0,0,0])).all():
				# print(correctImg[width,height]);
				regionsImage[width,height] = oriImg[width,height];
				markedColors.append((regionsImage[width,height,0],regionsImage[width,height,1],regionsImage[width,height,2])); #  output for average caculate
	print("average color is R:%f  G:%f  B:%f \n" % (sumNum_R,sumNum_G,sumNum_B));
	print(markedColors[:10]);

	global TextFolder;
	markedRegionColorFile = open( worktDir_+TextFolder+"markedRegionsText.txt", "wb");
	for index in range(len(markedColors)):
		string = "%d %d %d\\n"%(markedColors[index][0],markedColors[index][1],markedColors[index][2]);
		markedRegionColorFile.write(string);
	markedRegionColorFile.close();

	cv.namedWindow('correctImg',cv.WINDOW_NORMAL);
	cv.imshow('correctImg',correctImg);
	# os.getcwd();
	# listfile=os.listdir(os.getcwd());
	# print(listfile);
	cv.waitKey(10000);
	cv.destroyAllWindows();


if __name__ == '__main__':
   main(sys.argv)
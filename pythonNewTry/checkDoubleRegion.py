#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys
import cv2 as cv
import numpy as np
def main(argv):
	if len(argv) < 2:
		usage="Usage: \n 1 Parameters are needed:\n image file. "
		print(usage);
		return False;
	file_1 = argv[1];#	HE
	file_2 = argv[2];# EVG
	sourceImage_1 = cv.imread(file_1);
	sourceImage_2 = cv.imread(file_2);
	outputShape = (max(sourceImage_1.shape[0],sourceImage_2.shape[0]),max(sourceImage_1.shape[1],sourceImage_2.shape[1]),3);

	rows,cols = sourceImage_2.shape[:2];
	# ROTATE

	M = cv.getRotationMatrix2D((cols/2,rows/2),3,1);
	#第三个参数：变换后的图像大小
	sourceImage_2 = cv.warpAffine(sourceImage_2,M,(cols,rows));
	# MOVE
	# H=[1,0,tx
	#    0,1,ty]
	H = np.float32([[1,0,-300],
					[0,1,0]]);
	
	sourceImage_2 = cv.warpAffine(sourceImage_2,H,(cols,rows));

	outputImage = np.zeros(outputShape,dtype=np.uint8);
	outputImage[:sourceImage_1.shape[0],:sourceImage_1.shape[1],0]=sourceImage_1[:,:,0];
	outputImage[:sourceImage_2.shape[0],:sourceImage_2.shape[1],1]=sourceImage_2[:,:,1];
	cv.imwrite(r'C:/Users/kitrol/Desktop/Kiyasu lab/'+'double.png',outputImage);

if __name__ == '__main__':
    main(sys.argv)
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
	fileName = argv[1]; 
	sourceImage = cv.imread(fileName);
	shape = sourceImage.shape;
	baseName = fileName.split('.')[0];
	maskImage = np.zeros((shape[0],shape[1]),dtype=np.uint8);
	maskImage[::] = 255;
	index = np.where(np.average(sourceImage,axis=2)<=100);
	sourceImage[index] = [0,0,0];
	maskImage[index] = 0;

	cv.imwrite(baseName+'_b&w.png',sourceImage);
	cv.imwrite(baseName+'_mask.png',maskImage);
	del sourceImage;

	kernel = np.ones((5,5),np.uint8);
	dilation = cv.dilate(maskImage,kernel,iterations = 1);
	dilation = cv.dilate(dilation,kernel,iterations = 1);
	cv.imwrite(baseName+'_dilation.png',dilation);
	erosion = cv.erode(dilation,kernel,iterations = 1);
	erosion = cv.erode(erosion,kernel,iterations = 1);
	cv.imwrite(baseName+'_erosion.png',erosion);
	

	# erosion = cv.imread(r"C:\Users\kitrol\Desktop\2017SM01680_6_EVG_c3_lv_0_row_1_clo_1_erosion.png");
	# shape = erosion.shape;
	# resize = cv.resize(erosion, (int(shape[0]/10), int(shape[1]/10)), interpolation=cv.INTER_LANCZOS4);
	# cv.imwrite(r'C:\Users\kitrol\Desktop\2017SM01680_6_EVG_c3_lv_0_row_1_clo_1'+'_resize.png',resize);


if __name__ == '__main__':
    main(sys.argv)
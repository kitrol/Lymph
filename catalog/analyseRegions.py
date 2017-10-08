#!/usr/bin/python
# -*- coding: UTF-8 -*- 
#created by liangj

import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys
import os


def dealWithWhite(inputArray):
	output = [];
	for height in range(0,inputArray.shape[0]):
		for width in range(0,inputArray.shape[1]):
			if inputArray[height,width] != 255:
				output.append(inputArray[height,width]);
	return np.array(output);

def dealOneImage(image):
	B = dealWithWhite(image[:,:,0]);
	G = dealWithWhite(image[:,:,1]);
	R = dealWithWhite(image[:,:,2]);

	bmax = B.max();
	bmin = B.min();
	bmean = B.mean();

	gmax = G.max();
	gmin = G.min();
	gmean = G.mean();

	rmax = R.max();
	rmin = R.min();60
	rmean = R.mean();

	print("Blue  max min mean %f  %f  %f"%(bmax,bmin,bmean));
	print("Green  max min mean %f  %f  %f"%(gmax,gmin,gmean));
	print("Red  max min mean %f  %f  %f"%(rmax,rmin,rmean));


def main(argv):
	fileName = "D:\Lymph_Follicle\python\catalog\images";# JF14_091_S8_HE-2.png 

	folderFullName = "D:\Lymph_Follicle\python\catalog\images";
	for parent,dirnames,filenames in os.walk(folderFullName):
		for filename in filenames:
		# filename = filenames[0];
			print(filename+"\n");
			image = cv.imread(folderFullName+"\\"+filename);
			print(image.shape);
			dealOneImage(image);



if __name__ == '__main__':
   main(sys.argv)
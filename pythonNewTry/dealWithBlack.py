#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys
import cv2 as cv
import numpy as np
def progress_test():
    bar_length=20
    for percent in range(0, 100):
        hashes = '#' * int(percent/100.0 * bar_length)
        spaces = ' ' * (bar_length - len(hashes))
        sys.stdout.write("\rPercent: [%s] %d%%"%(hashes + spaces, percent))
        sys.stdout.flush()
        time.sleep(1)

def main(argv):
	if len(argv) < 2:
		usage="Usage: \n 1 Parameters are needed:\n image file. "
		print(usage);
		return False;
	fileName = argv[1]; 
	targetImage = cv.imread(fileName);
	baseName = fileName.split('.')[0];
	# print(targetImage.shape);
	# print(baseName);
	shape = targetImage.shape;
	for x in range(0,shape[0]):
		if x%100 == 0:
			sys.stdout.write("\r%d"%(x));
			sys.stdout.flush();
		for y in range(0,shape[1]):
			color = targetImage[x,y];
			# print(np.average(color));
			if np.average(color)<=100:
				targetImage[x,y] = [0,0,0];
	cv.imwrite(baseName+'_black.png',targetImage);

if __name__ == '__main__':
    main(sys.argv)
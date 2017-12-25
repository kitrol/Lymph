import openslide
import numpy as np
import cv2 as cv
from PIL import Image

import math
import time

time0 = time.time();
slide = openslide.OpenSlide('D:\\Lymph_Follicle\\newData\\JF14_044_S5_1_HE.svs');
print("detect_format "+slide.detect_format('D:\\Lymph_Follicle\\newData\\JF14_044_S5_1_HE.svs'));
print("slide dimensions is");
print(slide.dimensions);
print("slide level_dimensions is");
print(slide.level_dimensions);
print("slide level_downsamples is");
print(slide.level_downsamples);
print("slide get_best_level_for_sownsample is");
print(slide.get_best_level_for_downsample(3.0));
print("slide count is %d"%(slide.level_count));
level = 0;
outputChannel = 3;
bestResolution = slide.level_dimensions[level];
threshold = 3000;
maxSize = 20000;
if (bestResolution[0] > maxSize) or (bestResolution[1] > maxSize):
	rows = int(math.ceil(bestResolution[0]/threshold));
	columns = int(math.ceil(bestResolution[1]/threshold));
	targetImage = np.zeros([bestResolution[1],bestResolution[0],outputChannel],dtype=np.uint8);

	for x in range(0,rows):
		for y in range(0,columns):
			width = height = threshold;
			if (x+1)*threshold>bestResolution[0]:
				width = bestResolution[0]- x*threshold;
			if (y+1)*threshold>bestResolution[1]:
				height = bestResolution[1]- y*threshold;
			imagePiece = slide.read_region((x*threshold,y*threshold),level, (width,height),outputChannel);
			targetImage[y*threshold:y*threshold+height,x*threshold:x*threshold+width,:] = imagePiece;
			# cv.imwrite('D:\\Lymph_Follicle\\newData\\JF14_044_S5_2_HE_c%d_lv_%d_row_%d_clo_%d.png'%(outputChannel,level,x,y),imagePiece);
	cv.imwrite('D:\\Lymph_Follicle\\newData\\JF14_044_S5_1_HE_c%d_cv_%d.png'%(outputChannel,level),targetImage);
else:
	targetImage = slide.read_region((0,0),level, bestResolution,outputChannel);
	# print(targetImage.shape);
	cv.imwrite('D:\\Lymph_Follicle\\newData\\JF14_044_S5_1_HE_c%d_cv_%d.png'%(outputChannel,level),targetImage);

slide.close();
print("pasare image use time %d"%(time.time()-time0));



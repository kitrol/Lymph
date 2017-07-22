import cv2 as cv
import numpy as np
import globalVal as gl
import processOneImage as ps

def getArrayWithString(targetString):
	file = open(gl.worktDir_+gl.TextFolder+targetString, "r");
	string = file.read();
	file.close();
	array_1 = string.split("\n");
	result = [];
	for item in array_1:
		if len(item.split(","))>1:
			result.append([  np.uint8(item.split(",")[0]), 
		             	 	 np.uint8(item.split(",")[1]),
		                     np.uint8(item.split(",")[2]), ]);
	return np.array(result);

def mahalanobis_distance(A,cor_inv,B):
	result = np.sqrt(np.dot(np.dot(avg,inv_train_cor),target.T));
	return result;

def detectiveLymphFromNewTestData(newTestDataFileName,markedRegionRGB,markedRegionAvg):
	testData = ps.readImage(newTestDataFileName);

	# caculate the covariance's inverse matrix : inv_train_cor
	# markedRegionRGB : JF15_022_2_HE_region.csv
	file = open(gl.worktDir_+gl.TextFolder+markedRegionRGB, "r");
	string = file.read();
	trainProfileData = eval(string);
	file.close();
	trainData = getArrayWithString(trainProfileData);
	train_cor = np.cov(trainData.T);
	inv_train_cor = train_cor**-1;

	#  marked regions RGB data profile
	#  markedRegionProfile : JF15_022_2_HE_regionAvg&Var.txt
	file1 = open(gl.worktDir_+gl.TextFolder+markedRegionAvg, "r");
	string = file1.read();
	dict_1 = eval(string);
	file1.close();
	# print(dict_1);
	avgColor = np.array(dict_1['meanArray']);

	avg = np.array(dict_1['meanArray']);
	target = np.array([134,82,132]);
	print(np.sqrt(np.dot(np.dot(avg,inv_train_cor),target.T)));

	helpMatrix = np.zeros(testData.shape,dtype=np.uint8);
	helpMatrix[::] = 0;

	for width in range(0,testData.shape[0]):
		for height in range(0,testData.shape[1]):
			if isAlmostWhite(testData[width,height])==False:
				R = testData[width,height,0];
				G = testData[width,height,1];
				B = testData[width,height,2];
				distance = mahalanobis_distance(avgColor,inv_train_cor,np.array([R,G,B]));
				if distance > gl.THRESHOLD:
					helpMatrix[width,height] = np.array([255,255,255]);
				else:
					helpMatrix[width,height] = np.array([R,G,B]);

	cv.imwrite(gl.worktDir_+gl.TextFolder+"123.bmp",helpMatrix);



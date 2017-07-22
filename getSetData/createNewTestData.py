import cv2 as cv
import numpy as np
import globalVal as gl
import processOneImage as ps


def getNewTestData(testDataFileName,trainTextFile):
	testData = ps.readImage(testDataFileName);
	notWhiteColors = [];
	for width in range(0,testData.shape[0]):
		for height in range(0,testData.shape[1]):
			if isAlmostWhite(testData[width,height])==False:
				notWhiteColors.append((testData[width,height,0],testData[width,height,1],testData[width,height,2]));

	notWhiteAverage=np.array(notWhiteColors);
	testDataProfile = ps.caculateAverageAndVarianceForRGB(notWhiteAverage);

	file = open(gl.worktDir_+gl.TextFolder+trainTextFile, "r");
	string = file.read();
	trainProfileData = eval(string);
	# print(trainProfileData);
	file.close();
	# print(type(trainProfileData['meanArray'][0]));

	mean_train_R = trainProfileData['meanArray'][0];
	mean_train_G = trainProfileData['meanArray'][1];
	mean_train_B = trainProfileData['meanArray'][2];

	variance_train_R = trainProfileData['variance'][0];
	variance_train_G = trainProfileData['variance'][1];
	variance_train_B = trainProfileData['variance'][2];

	standardDeviation_train_R = trainProfileData['standardDeviation'][0];
	standardDeviation_train_G = trainProfileData['standardDeviation'][1];
	standardDeviation_train_B = trainProfileData['standardDeviation'][2];


	mean_test_R = testDataProfile['meanArray'][0];
	mean_test_G = testDataProfile['meanArray'][1];
	mean_test_B = testDataProfile['meanArray'][2];

	variance_test_R = testDataProfile['variance'][0];
	variance_test_G = testDataProfile['variance'][1];
	variance_test_B = testDataProfile['variance'][2];

	standardDeviation_test_R = testDataProfile['standardDeviation'][0];
	standardDeviation_test_G = testDataProfile['standardDeviation'][1];
	standardDeviation_test_B = testDataProfile['standardDeviation'][2];

	for width in range(0,testData.shape[0]):
		for height in range(0,testData.shape[1]):
			if isAlmostWhite(testData[width,height])==False:
				new_R = ((testData[width,height,0]-mean_test_R)*standardDeviation_train_R/standardDeviation_test_R)+mean_train_R;
				new_G = ((testData[width,height,1]-mean_test_G)*standardDeviation_train_G/standardDeviation_test_G)+mean_train_G;
				new_B = ((testData[width,height,2]-mean_test_B)*standardDeviation_train_B/standardDeviation_test_B)+mean_train_B;
				testData[width,height] = np.array([np.uint8(new_R),np.uint8(new_G),np.uint8(new_B)]);

	fileName = testDataFileName.split('.')[0];
	cv.imwrite(gl.worktDir_+gl.newTestFolder+fileName+'_new.bmp',testData);

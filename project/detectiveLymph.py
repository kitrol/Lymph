import cv2 as cv
import numpy as np
import globalVal as gl
import processOneImage as ps
from skimage import io,measure,color

def getArrayWithString(targetString):
	array_1 = targetString.split("\n");
	result = [];
	for item in array_1:
		if len(item.split(","))>1:
			result.append([  np.uint8(item.split(",")[0]), 
		             	 	 np.uint8(item.split(",")[1]),
		                     np.uint8(item.split(",")[2]), ]);
	return np.array(result);

def mahalanobis_distance(A,cor_inv,B):
	result = np.sqrt(np.dot(np.dot(A,cor_inv),B.T));
	return result;

def labelingGrayImage(imageMatrix):
	gray = color.rgb2gray(imageMatrix);
	labeledPic,regionsCnt = measure.label(gray,background=255,return_num=True,connectivity=2);
	props = measure.regionprops(labeledPic);
	# print("regions is ",regionsCnt);
	cv.imwrite(gl.outputFolder+"colored.bmp",labeledPic);
	# print(props[0]);
	return props;

def detectiveLymphFromNewTestData(newTestDataFileName,markedRegionRGB,markedRegionAvg,usingTraindata):
	print("***********  check for %s start  ***********"%(newTestDataFileName));
	fileDir = gl.newTestFolder;
	if usingTraindata==True:
		fileDir = gl.TrainFolder;

	testData = ps.readImage(fileDir+newTestDataFileName);
	kernel = np.ones((5,5),np.uint8);

	# ####    caculate the covariance's inverse matrix : inv_train_cor
	# ####    markedRegionRGB : JF15_022_2_HE_region.csv
	file = open(gl.TextFolder+markedRegionRGB, "r");
	string = file.read();
	file.close();
	trainData = getArrayWithString(string);
	train_cor = np.cov(trainData.T);
	inv_train_cor = train_cor**-1;

	#  marked regions RGB data profile
	#  markedRegionProfile : JF15_022_2_HE_regionAvg&Var.txt
	file1 = open(gl.TextFolder+markedRegionAvg, "r");
	string_1 = file1.read();
	dict_1 = eval(string_1);
	file1.close();
	print(dict_1);
	avgColor = np.array(dict_1['meanArray']);

	avg = np.array(dict_1['meanArray']);
	print("avg is ",avg);
	target = np.array([134,82,132]);
	print(np.sqrt(np.dot(np.dot(avg,inv_train_cor),target.T)));

	helpMatrix = np.zeros(testData.shape,dtype=np.uint8);
	helpMatrix[::] = 0;

	for width in range(0,testData.shape[0]):
		for height in range(0,testData.shape[1]):
			if ps.isAlmostWhite(testData[width,height])==False:
				R = testData[width,height,0];
				G = testData[width,height,1];
				B = testData[width,height,2];
				distance = mahalanobis_distance(avgColor,inv_train_cor,np.array([R,G,B]));
				if distance <= gl.THRESHOLD:
					helpMatrix[width,height] = np.array([R,G,B]);

	cv.morphologyEx(helpMatrix, cv.MORPH_OPEN, kernel);#  开运算 去噪音
	cv.morphologyEx(helpMatrix, cv.MORPH_CLOSE, kernel); # 填充小洞
	
	ret,img = cv.threshold(helpMatrix,0,255,cv.THRESH_BINARY_INV);
	img = cv.blur(img,(13,13));
	cv.dilate(img,kernel,iterations = 2);
	ret,img = cv.threshold(img,125,255,cv.THRESH_BINARY);
	print(img.shape);
	# ret,img = cv.threshold(img,0,255,cv.THRESH_BINARY_INV);
	
	ps.showImageInWindow("1",1000,helpMatrix);
	cv.imwrite(gl.outputFolder+newTestDataFileName.split(".")[0]+"_tryMark.bmp",helpMatrix);
	cv.imwrite(gl.outputFolder+newTestDataFileName.split(".")[0]+"_tryMarkGray.bmp",img);
	print("*********** mark suspicous region to : "+gl.outputFolder+newTestDataFileName.split(".")[0]+"_tryMark.bmp"+" **************");

	regions = labelingGrayImage(img);
	correctImageName = "JF15_022_2_HE_correct.bmp";
	img_2 = cv.imread(correctImageName);
	print("*********** separated as : %d regions ***********"%(len(regions)));
	for index in range(len(regions)):
		centroid = regions[index].centroid;
		bbox = regions[index].bbox;#(min_row, min_col, max_row, max_col)
		max_x = bbox[3]-bbox[1];
		max_y = bbox[2] - bbox[0];
		size = max_x*max_y;
		r = max(max_x,max_y);
		ratio = min(max_x,max_y)/r; 

		if r<=gl.MAX_SIZE and ratio>=gl.MIN_RATIO:
			cv.circle(testData,(int(centroid[1]),int(centroid[0])), r, (0,255,0), 2);

	cv.imwrite(gl.outputFolder+newTestDataFileName.split(".")[0]+"circled.bmp",testData);
	print("*********** write pic File to : "+gl.outputFolder+newTestDataFileName.split(".")[0]+"circled.bmp"+" **************");
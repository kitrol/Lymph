import cv2 as cv
import numpy as np
import globalVal as gl


# expand balck regions
def erodeOrin(oriImg,erodeMask):
	for width in range(0,oriImg.shape[0]):
		for height in range(0,oriImg.shape[1]):
			if (erodeMask[width,height]==np.array([0,0,0])).all():
				oriImg[width,height] = np.array([0,0,0]);


def showImageInWindow(windowName,time,image):
	cv.namedWindow(windowName,cv.WINDOW_NORMAL);
	cv.imshow(windowName,image);
	cv.waitKey(time);
	cv.destroyAllWindows();

def readImage(fileName,withColor=1):
	img = cv.imread(fileName);
	return img;

def isAlmostWhite(rgbColor):
	if (255-rgbColor[0]<=25)and(255-rgbColor[1]<=25)and(255-rgbColor[2]<=25): # if all RGB value is greater than 230 it means this pixel is white
		return True;
	return False;

def caculateAverageAndVarianceForRGB(numpyArray):
	# array's shape should be (n,3); n lines with 3 columns
	sumArray=np.array([numpyArray[:,0].sum(),numpyArray[:,1].sum(),numpyArray[:,2].sum()],dtype=np.float);
	lines = float(numpyArray.size/3);
	meanValue = np.array(sumArray/lines);
	meanArray = np.zeros(numpyArray.shape);
	meanArray[:,0] = meanValue[0]; 
	meanArray[:,1] = meanValue[1]; 
	meanArray[:,2] = meanValue[2];
	temp = (numpyArray-meanArray)**2;
	variance = np.array([temp[:,0].sum(),temp[:,1].sum(),temp[:,2].sum()],dtype=np.float)/lines;
	standardDeviation = variance**(1/2);
	result = {"meanArray":list(meanValue),"variance":list(variance),"standardDeviation":list(standardDeviation)};
	return result;

def wirteRGBToFile(targetFileName,rgbData):
	file = open(targetFileName, "w+");
	string = '';
	for index in range(len(rgbData)):
		string += "%d,%d,%d\n"%(rgbData[index][0],rgbData[index][1],rgbData[index][2]);
	file.write(string);
	file.close();

def writeStringToFile(targetFileName,stringData):
	file = open(targetFileName, "w+");
	file.write(stringData);
	file.close();
	pass

def processOneTrainImage(trainImageName,correctImageName):
	print("processOneTrainImage  start for Image: "+trainImageName);
	oriImg = readImage(gl.TrainFolder+trainImageName);
	correctImg = readImage(gl.TrainFolder+correctImageName);
	imageName_ = trainImageName.split('.')[0];

	print("processOneTrainImage  ***erode marked regions*** for Image: "+trainImageName);
	ret,img_gray = cv.threshold(correctImg,0,255,cv.THRESH_BINARY); # gray image for marked regions still be black

	# kernel = np.ones((5,5),np.uint8);
	# img_gray_erode = cv.erode(img_gray,kernel,iterations=1);  # expand the edge for marked regions
	# erodeOrin(correctImg,img_gray_erode);

	print("processOneTrainImage  marked regions for Image: "+trainImageName);
	# regionsImage = np.zeros(correctImg.shape,dtype=np.uint8);  # regions with color and bg is black
	maskImage = np.zeros(correctImg.shape,dtype=np.uint8);    # regions with color and bg is white
	maskImage[::] = 255;
	markedColors = [];
	notWhiteColors = [];

	for width in range(0,oriImg.shape[0]):
		for height in range(0,oriImg.shape[1]):
			if (correctImg[width,height]==np.array([0,0,0])).all():
				# print(correctImg[width,height]);
				# regionsImage[width,height] = oriImg[width,height];
				maskImage[width,height] = oriImg[width,height];
				markedColors.append([oriImg[width,height,0],oriImg[width,height,1],oriImg[width,height,2]]); #  output for average caculate
				notWhiteColors.append((oriImg[width,height,0],oriImg[width,height,1],oriImg[width,height,2]));
			elif isAlmostWhite(oriImg[width,height])==False: #caculate the average value for train image
				notWhiteColors.append((oriImg[width,height,0],oriImg[width,height,1],oriImg[width,height,2]));

	print("processOneTrainImage  ***caculate average and variance and standard devision *** for Image: "+trainImageName);
	markedAverage=np.array(markedColors);
	notWhiteAverage=np.array(notWhiteColors);
	retultRegion = caculateAverageAndVarianceForRGB(markedAverage);
	resultWhole = caculateAverageAndVarianceForRGB(notWhiteAverage);
	# cv.imwrite(gl.worktDir_+gl.TextFolder+imageName_+"_regionsImage.bmp",regionsImage);
	cv.imwrite(gl.TextFolder+imageName_+"_maskImage.bmp",maskImage);

	# print(retultRegion['meanArray']);
	# print(retultRegion['variance']);
	# print(resultWhole['meanArray']);
	# print(resultWhole['variance']);

	fileName_1 =gl.TextFolder+imageName_+"_region.csv";
	fileName_2 =gl.TextFolder+imageName_+"_notWhite.csv";
	fileName_3 =gl.TextFolder+imageName_+"_regionAvg&Var.txt";
	fileName_4 =gl.TextFolder+imageName_+"_notWhiteAvg&Var.txt";

	wirteRGBToFile(fileName_1,markedColors);
	wirteRGBToFile(fileName_2,notWhiteColors);
	writeStringToFile(fileName_3,str(retultRegion));
	writeStringToFile(fileName_4,str(retultRegion));
	print("processOneTrainImage  ***save details as text*** for Image: "+trainImageName);
	showImageInWindow("1",1000,maskImage);

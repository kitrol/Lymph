# from keras.models import Sequential
# from keras.layers import Dense, Activation

# model = Sequential()
# model.add(Dense(32, input_shape=(784,)))
# model.add(Activation('relu'))
# model.add(Dense(10))
# model.add(Activation('softmax'))

import cv2
import numpy as np


listArray = [[1,2,3],[4,5,6],[7,8,9],[10,11,12]];
npArray_1 = np.array([[1,2,3],[4,5,6],[7,8,9],[10,11,12]]);
npArray_2 = np.array([1,1,1]);
print(npArray_1.size/3);

# maskImage = np.zeros((13,240,3));
# maskImage[::,0] = 255;
# print(maskImage[13:13:1]);

sumArray = np.array([npArray_1[:,0].sum(),npArray_1[:,1].sum(),npArray_1[:,2].sum()]);
meanArray = np.zeros(npArray_1.shape);
temp = np.array(sumArray/float(npArray_1.size/3));
meanArray[:,0] = temp[0];
meanArray[:,1] = temp[1];
meanArray[:,2] = temp[2];
mean = np.array(temp);
temp_2 = (npArray_1-meanArray)**2;
# np.array([(npArray_1-meanArray)**2[:,0].sum(),(npArray_1-meanArray)**2[:,1].sum(),(npArray_1-meanArray)**2[:,2].sum()]);
variance = np.array([temp_2[:,0].sum(),temp_2[:,1].sum(),temp_2[:,2].sum()])/float(npArray_1.size/3);

print(sumArray);
print(mean);
print(variance);


# temp = np.zeros((5,6,3));
# temp[:5, 0:,0] = 11;
# temp[:5, :3,1] = 12;
# temp[:5, 0:,2] = 13;
# print(temp);

# meanArray = np.full(npArray_1.size/3,sumArray/float(npArray_1.size/3));



# temp = npArray_1 - npArray_2;
# print(temp);

# file = open("/Users/liangjun/Desktop/123.txt",'wb');
# file.write("%d %d %d\n"%(listArray[0][0],listArray[1][1],listArray[2][2]));
# file.close();



###  read image test
# img = cv2.imread("/Users/liangjun/Desktop/JF15_022_2_HE.bmp");

# img = cv2.GaussianBlur(img,(3,3),0);
# # img=img[:,:,0];
# # img[:,:,2]=0;
# canny = cv2.Canny(img, 100, 150);

# # cv2.namedWindow("canny",cv2.WINDOW_NORMAL);
# # cv2.imshow("canny", canny);
# cv2.imwrite("/Users/liangjun/Desktop/edge.bmp", canny);
# print(img.shape);
# print(img.size);

# print(canny.shape);
# print(canny.size);

# for width in range(canny.shape[0]):
# 	for height in range(canny.shape[1]):
# 		if canny[width,height] > 0:
# 			img[width,height] = (255,255,255);
# 			pass
	

# # print("width is ",canny.width);
# cv2.imwrite("/Users/liangjun/Desktop/edge_2.bmp", img);


# cv2.waitKey(10000);
# cv2.destroyAllWindows();

####  camera use test
# cap = cv2.VideoCapture(0);

# while(True):
# 	ret, frame = cap.read();
# 	# Our operations on the frame come here
# 	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY);

# 	# Display the resulting frame
# 	cv2.imshow('frame',gray);
# 	if cv2.waitKey(1) & 0xFF == ord('q'):
# 		break

#  # When everything done, release the capture
# cap.release();
# cv2.destroyAllWindows();


#####  save video test
# cap = cv2.VideoCapture(0)
# # Define the codec and create VideoWriter object
# fourcc = cv2.cv.FOURCC(*'XVID')
# out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

# while(cap.isOpened()):
# 	ret, frame = cap.read()
# 	if ret==True:
# 		frame = cv2.flip(frame,0)
# 		# write the flipped frame
# 		out.write(frame);
# 		cv2.imshow('frame',frame)
# 		if cv2.waitKey(1) & 0xFF == ord('q'):
# 			break;
# 	else:
# 		break;

# # Release everything if job is finished
# cap.release()
# out.release()
# cv2.destroyAllWindows()












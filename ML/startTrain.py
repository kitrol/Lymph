#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys,os
import cv2 as cv
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn import svm
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
import pickle

def predictForData(model,targetData,labels):
	y_pred = model.predict(targetData);
	accuracy = model.score(targetData, labels);
	Cm = confusion_matrix(labels, y_pred);
	precision, recall, fscore, support = precision_recall_fscore_support(labels, y_pred, average='macro');
	# print("precision %f recall %f fscore %f"%(precision,recall,fscore));
	return precision, recall, fscore, accuracy;

def readTrainFile(fileName):
	file = open(fileName, "r");
	srcString = file.read();
	file.close();
	matrix = [];
	array = srcString.split("\n");
	for line in array:
		if (len(line)>1):
			matrix.append([float(num) for num in line.split(",")]);
	data = np.array(matrix);
	return data;

def saveModel(model,featureNum):
	fileName = os.path.join(r'C:\Users\kitrol\Desktop\MachineLearning\models','model_%d.pickle'%int((featureNum-1)/3));
	if os.path.isfile(fileName):
		os.remove(fileName);
	with open(fileName, 'wb') as modelFile:
		pickle.dump(model,modelFile);

def main(argv):
	if len(argv) < 2:
		usage="Usage: \n 1 Parameters are needed:\n train **.csv file needed "
		print(usage);
		return False;
	randomSeed = 123123;
	fileName = argv[1];
	trainData = readTrainFile(fileName);
	features = trainData[:,:-1];
	truth = trainData[:,-1];
	X_train, X_eval, y_train, y_eval = train_test_split(features, truth, test_size=0.6, random_state=randomSeed);
	X_cv, X_test, y_cv, y_test       = train_test_split(X_eval, y_eval, test_size=0.5, random_state=randomSeed)

	clf = MLPClassifier(activation='relu', alpha=1e-05, batch_size='auto',
       					beta_1=0.9, beta_2=0.999, early_stopping=False,
       					epsilon=1e-08, hidden_layer_sizes=(1000,1000,1000), learning_rate='invscaling',  #(20,20,20,20,10,5)
       					learning_rate_init=0.001, max_iter=2000,
       					nesterovs_momentum=True, power_t=0.5, random_state=1, shuffle=True,
       					solver='adam', tol=0.00001, validation_fraction=0.2, verbose=False,
       					warm_start=False)
	clf.fit(X_train, y_train);
	precision_train,recall_train,fscore_train,accuracy_train = predictForData(clf,X_train,y_train);
	precision_cv,recall_cv,fscore_cv,accuracy_cv = predictForData(clf,X_cv,y_cv);
	precision_test,recall_test,fscore_test,accuracy_test =predictForData(clf,X_test,y_test);

	# print("precision %f,%f,%f\n"%(precision_train,precision_cv,precision_test));
	# print("recall %f,%f,%f\n"%(recall_train,recall_cv,recall_test));
	print("fscore %f,%f,%f\n"%(fscore_train,fscore_cv,fscore_test));
	print("accuracy %f,%f,%f\n"%(accuracy_train,accuracy_cv,accuracy_test));
	
	# print(features.shape);
	# features.shape[0] : m train data
	# features.shape[1] : n features for one data (bias item included)
	saveModel(clf,features.shape[1]);
	# trained model write to file

if __name__ == '__main__':
    main(sys.argv)
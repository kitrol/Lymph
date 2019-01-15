#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned
import sys
import os
import shutil

def changeNamesInFolder(folderName):
	if os.path.exists(folderName):
		for f in os.listdir(folderName):
			if f.find(r'- 副本') >= 0 :
				newName = f.replace(r' - 副本','_train');
				print(newName);
				shutil.move(os.path.join(folderName,f), os.path.join(folderName,newName));
def changeNamesWithFolder(folderName):
	folder = os.path.basename(folderName);
	if os.path.exists(folderName):
		for f in os.listdir(folderName):
			if f.find(r'.png') >= 0 :
				newName = folder+"_"+f;
				print(newName);
				shutil.move(os.path.join(folderName,f), os.path.join(folderName,newName));

def relistFiles(argv):
	subFolders = argv[1:-1];
	outputFolder = argv[-1];
	if not os.path.exists(outputFolder):
		os.mkdir(outputFolder);
	FileCounter = 1;
	for subFolder in subFolders:
		if os.path.exists(subFolder):
			for f in os.listdir(subFolder):
				filePath = os.path.join(subFolder,f);
				if os.path.isfile(filePath):
					fileFormat = os.path.basename(filePath).split('.')[1];
					if fileFormat != "txt":
						originalName = os.path.basename(filePath).split('_')[0];
						if originalName == os.path.basename(filePath):
							originalName = "No";
						newFileName = originalName+"-%d.%s"%(FileCounter,fileFormat);
						newFullPath = os.path.join(outputFolder,newFileName);
						shutil.move(filePath,newFullPath);
						FileCounter += 1;
def main(argv):
	# relistFiles(argv);
	# changeNamesInFolder(argv[1]);
	changeNamesWithFolder(argv[1]);


if __name__ == '__main__':
    main(sys.argv)
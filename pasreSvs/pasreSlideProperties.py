#!/usr/bin/python
# -*- coding: UTF-8 -*- 

import json
import demjson
import re
import sys
import os

filePath_ = '';
targetFileName = "";
propertyFileName_ = 'D:/testout.txt';
showDetialFile = 'D:/2016/openslide-win64-20170711-nightly/bin/openslide-show-properties.exe';
outputPngTool = 'D:/2016/openslide-win64-20170711-nightly/bin/openslide-write-png.exe';
# print(type(all_the_text)); D:\2016\openslide-win64-20170711-nightly\bin\openslide-write-png.exe D:\2016\ori_slide\JF15_022_2_HE.svs 0 0 3 2306 1264 D:\2016\123.png

def pasurePropertyFile( filePath ):
	detialFile = open(propertyFileName_, "r");
	all_the_text = detialFile.read();
	start = all_the_text.find("openslide.level-count");
	end = all_the_text.find("tiff.ImageDescription");
	# print(start,"   ",end);
	dictStr = json.dumps(all_the_text[start:end]);
	# print('before \n'+dictStr);
	dictStr = dictStr.split(r'\n');
	# print(dictStr);
	# for x in range(0,len(dictStr)-1):
	# 	print(dictStr[x]);
	openslide = {};
	openslide['level-count'] = int((dictStr[0].split(r': ')[1]).replace("'", ""));
	openslide['level'] = [];
	for index in range(0,openslide['level-count']):
		openslide['level'].append({});
		openslide['level'][index]['downsample'] = float((dictStr[(index)*5+1].split(r': ')[1]).replace("'", ""));
		openslide['level'][index]['height'] =     int((dictStr[(index)*5+2].split(r': ')[1]).replace("'", ""));
		openslide['level'][index]['tile-height'] =int((dictStr[(index)*5+3].split(r': ')[1]).replace("'", ""));
		openslide['level'][index]['tile-width'] = int((dictStr[(index)*5+4].split(r': ')[1]).replace("'", ""));
		openslide['level'][index]['width'] =      int((dictStr[(index)*5+5].split(r': ')[1]).replace("'", ""));

	openslide['quickhash'] = (dictStr[24].split(r': ')[1]).replace("'", "");
	# print(openslide);
	return openslide;

def outputPngFile(propertyForfile,levelIndex):
	start_x = 0;
	start_y = 0;
	width = propertyForfile['level'][levelIndex]['width'];
	height = propertyForfile['level'][levelIndex]['height'];
	global filePath_;
	global targetFileName;
	print(targetFileName);
	outputFileName = filePath_+'/outputFile.png';
	# 0 0 3 2306 1264 D:\2016\123.png
	cmdStr = outputPngTool+" "+targetFileName+" 0 0 %d %d %d %s" % (levelIndex,width,height,outputFileName);
	print(cmdStr);
	print(os.system(cmdStr));


# read file and show properties
def main(argv):
	global filePath_;
	filePath_ = os.path.dirname(argv[0]);
	global targetFileName;
	targetFileName = argv[1];
	print(type(targetFileName));
	if isinstance(targetFileName, str)!=True:
		print("first argv should be slide file with .svs on the end of file!");
		sys.exit();
	
	# output property file as propertyFileName_;
	print(os.system(showDetialFile+" "+targetFileName+">"+propertyFileName_));

	# read property file into memory
	propertyFile = pasurePropertyFile(propertyFileName_);
	for index in range(0,propertyFile['level-count']):
		print("level ",index," property width ",propertyFile['level'][index]['width'],"  height ",propertyFile['level'][index]['height']);

	print("choose the scale you want to out put from 1 to ",propertyFile['level-count']);
	index = input("Enter your input: ");
	while (index.isdigit() and int(index)>=1 and int(index) <= 4) != True:
		index = input("Enter your input: ");
	index = int(index)-1;
	print("target reseluton is ",propertyFile['level'][index]['width']," * ",propertyFile['level'][int(index)]['height'],"=",propertyFile['level'][int(index)]['width']*propertyFile['level'][int(index)]['height']);	
	outputPngFile(propertyFile,int(index));

if __name__ == '__main__':
    main(sys.argv)
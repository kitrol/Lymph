# -*- coding: utf-8 -*- 
import sys
import subprocess
import os

# steps 
# 1 read file 
# delete chinses charactors
# encrypt
# save file

#test files
srcFile = "/Users/liangjun/Desktop/main1.lua";
desFile = "/Users/liangjun/Desktop/main2.lua";
#test files

srcFolder = "/Users/liangjun/Documents/cocos2d-x-3.2/project/newbingo/originalSrc";
targetFolder = "/Users/liangjun/Desktop/encryptTest";
DECRYPTFolder = "/Users/liangjun/Desktop/decryptTest";

salt_table = [-5,-3,15,8,19,1,21,13,6,-1];
_xxteaSign = "bingo";

srcLength =2123;

def ENCRYPT (src):
	srcLength = len(src);
	targetStr = "";
	for index in xrange(0,srcLength):
		char = src[index];
		x = ord(char);
		salt = salt_table[index%10];
		x = (x+56+salt)%(128);
		char = chr(x);
		targetStr += char;
	return targetStr;
	

def DECRYPT (str):
	srcLength = len(str);
	targetStr = "";
	for index in xrange(5,srcLength):
		char = str[index];
		salt = salt_table[(index-5)%10];
		key = (128)-(56+salt);
		x = ord(char);
		x = (x+key)%(128);
		char = chr(x);
		targetStr += char;
	return targetStr;

def SAVE_FILE(fileStr,fileName):
	fileHandle = open(fileName,'w');
	fileHandle.write(fileStr);
	fileHandle.close();

def getAsciiStr(sourceStr):
	return sourceStr.decode('ascii', 'ignore');

# 测试部分
# srcHandle = open(srcFile,'rb');
# srcString = srcHandle.read();
# s = srcString.decode('ascii', 'ignore');
# print(s);
# test = '---- 下面的变量仍旧延续“bingo” 字段';
# print(test.decode('ascii', 'ignore'));

# encrypt = _xxteaSign+ENCRYPT(getAsciiStr(s));
# SAVE_FILE(encrypt,desFile);

# # print("after encrypt is \n%s"%(encrypt));
# decryptStr = DECRYPT(encrypt);
# # print("after decrypt is \n%s"%(decryptStr));
# srcHandle.close();



for luafile in os.listdir(srcFolder):
	fileName = srcFolder+"/"+luafile;
	if fileName.find(".lua") >= 0:
		srcHandle = open(fileName,'r');
		srcString = srcHandle.read();
		s = srcString.decode('ascii','ignore');
		encrypt = _xxteaSign+ENCRYPT(s);
		targetFileName = targetFolder+"/"+luafile
		SAVE_FILE(encrypt,targetFileName);
		srcHandle.close();


for luafile in os.listdir(targetFolder):
	fileName = targetFolder+"/"+luafile;
	srcHandle = open(fileName,'r');
	srcString = srcHandle.read();
	encrypt = DECRYPT(srcString);
	targetFileName = DECRYPTFolder+"/"+luafile
	SAVE_FILE(encrypt,targetFileName);
	srcHandle.close();



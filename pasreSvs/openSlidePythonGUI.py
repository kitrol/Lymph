#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created By Liang Jun Copyright owned

import openslide
import sys
import os
import numpy as np
import cv2 as cv
from PIL import Image
import math
import time
import platform
import shutil
import threading
import multiprocessing


try:
	from tkinter import *
except ImportError:  #Python 2.x
	PythonVersion = 2
	import Tkinter as tk
	from Tkinter import *
	import ttk
	import tkFileDialog as filedialog
	import tkMessageBox as messagebox
else:  #Python 3.x
	PythonVersion = 3
	import tkinter as tk
	from tkinter import ttk
	import tkinter.filedialog as filedialog
	import tkinter.messagebox as messagebox

MultiThread = False;
MultiProcess = False;
PROCESS_COUNT = 0;
CORES = 1;
LOCK = threading.Lock();
CURRENT_FILE_NAME = None

def isMultiThread():
	global MultiThread;
	MultiThread = not MultiThread;
def isMultiProcess():
	global MultiProcess;
	MultiProcess = not MultiProcess;
def outputModeClassifier(outputSize):
	# threshold = 70000;
	threshold = 1;
	if (outputSize[0] > threshold) or (outputSize[1] > threshold):
		return "RangeMode";
	else:
		return "PieceMode";

def getRealRectForOutput(originalResl,thumbnilRect,thumbnilSize):
	startX = math.floor((thumbnilRect[0]/thumbnilSize[0])*originalResl[0]);
	endX   = math.ceil((thumbnilRect[2]/thumbnilSize[0])*originalResl[0]);
	startY = math.floor((thumbnilRect[1]/thumbnilSize[1])*originalResl[1]);
	endY   = math.ceil((thumbnilRect[3]/thumbnilSize[1])*originalResl[1]);
	return (startX,startY,endX-startX,endY-startY);

def initOutputFolder(mainFolderName,outputMode,level,rectArray,channel,pieceSize):
	Mode = "Range";
	subfolders = [];
	if outputMode == "By Piece":
		Mode = "Piece";
	if not os.path.exists(mainFolderName):
		# create main output folder
		os.mkdir(mainFolderName);	
	# create sub folder for all outputs
	for rect in rectArray:
		# rect = (startx starty width height);
		subFolderName = "%s_lv%d_(%d_%d_%d_%d)_ch_%d_ps_%d"%(Mode,level,rect[0],rect[1],rect[2],rect[3],channel,pieceSize);
		subFolderName = os.path.join(mainFolderName,subFolderName);
		subfolders.append(subFolderName);
		if os.path.exists(subFolderName):
			for f in os.listdir(subFolderName):
				filePath = os.path.join(subFolderName,f);
				if os.path.isfile(filePath):	
					os.remove(filePath);
		else:
			os.mkdir(subFolderName);
	return subfolders;

def pieceDetailFile(outputDir,width,height,pieceSize,rows,columns):
	file = open(os.path.join(outputDir,"des.txt"), "w+");
	string = 'width:%d\nheight:%d\npieceSize:%s\n\rrows:%d\ncolumns:%d'%(width,height,str(pieceSize),rows,columns);
	file.write(string);
	file.close();

def outputThumbnail(slide,outputDir,channel):
	fileName = outputDir+'Thumbnail_ch%d.png'%(channel);
	temp=list(slide.level_dimensions);
	temp.reverse();
	targetRes = None;
	level = len(temp)-1;
	for index in range(len(temp)):
		res = temp[index];
		if res[0]>=1920:
			targetRes = res;
			level = len(temp)-index-1;
			break;
	if targetRes == None:
		targetRes = slide.level_dimensions[len(slide.level_dimensions)-1];
		level = len(slide.level_dimensions)-1;
	outputThumbnail = slide.read_region((0,0),level, targetRes,channel);
	cv.imwrite(os.path.join(outputDir,'Thumbnail_ch%d.png'%(channel)),outputThumbnail);
def progressShow(current,timeCost,total):
	bar_length = 30;
	percent = (float(current)/total);
	hashes = '*' * int(percent * bar_length);
	spaces = '-' * (bar_length - len(hashes));
	sys.stdout.write("\r[%s] %d%% Processing %d/%d time used %ds"%(hashes+spaces,percent*100,current,total,timeCost));
	sys.stdout.flush();
	return percent;

def readAndWrite(fileName,rectAndPathArray,level,channel,counter,processLock,total):
	time0 = time.time();
	slide = openslide.OpenSlide(fileName);
	for item in rectAndPathArray:
		rect = item[0];
		path = item[1];
		targetImage = slide.read_region((rect[0],rect[1]),level, (rect[2],rect[3]),channel);
		cv.imwrite(path,targetImage);
		del targetImage;
		processLock.acquire();
		counter.value += 1;
		progressShow(counter.value,time.time()-time0,total);
		processLock.release();
	

def outputImageByRange(slide,level,channel,outputFormat,outputPath,rangeRect,pieceSize=0):
	# rangeRect:[startX startY width height]
	time0 = time.time();
	startX = int(rangeRect[0]);
	startY = int(rangeRect[1]);
	rangeWidth = int(rangeRect[2]);
	rangeHeight = int(rangeRect[3]);
	columns = int(math.ceil(rangeRect[2]/float(pieceSize)));
	rows = int(math.ceil(rangeRect[3]/float(pieceSize)));
	pieceDetailFile(outputPath,rangeWidth,rangeHeight,pieceSize,rows,columns);
	total = rows*columns;
	bestSize = slide.level_dimensions[0];
	targetSize = slide.level_dimensions[level];
	def getStartPos(bestReso,targetReso,relativeX,relativeY):
		real_x = int((float(relativeX)/targetReso[0])*bestReso[0]);
		real_y = int((float(relativeY)/targetReso[1])*bestReso[1]);
		return (real_x,real_y);
	############################################ Multiprocessing   Test ############################################
	global MultiThread,CURRENT_FILE_NAME,MultiProcess,CORES;
	if MultiProcess:
		print("###################### Mode MultiProcess ######################");
		progressShow(0,0,total);
		processCounter = multiprocessing.Value("i",0);
		lock = multiprocessing.Lock();
		rectGroup = [];
		maxProgressCnt = CORES;
		for x in range(maxProgressCnt):
			rectGroup.append([]);
		for y in range(0,rows):
			for x in range(0,columns):
				width = height = pieceSize;
				if (x+1)*pieceSize>rangeWidth:
					width = rangeWidth- x*pieceSize;
				if (y+1)*pieceSize>rangeHeight:
					height = rangeHeight- y*pieceSize;
				x_1 = startX+x*pieceSize;
				y_1 = startY+y*pieceSize;
				realPos = getStartPos(bestSize,targetSize,x_1,y_1);
				index = (y)*columns+(x+1);
				rect = (realPos[0],realPos[1],width,height);
				path = os.path.join(outputPath,'_c%d_lv_%d_row_%d_clo_%d%s'%(channel,level,y,x,outputFormat));
				rectGroup[(index-1)%(maxProgressCnt)].append([rect,path]);
		for rectsArray in rectGroup:
			p = multiprocessing.Process(target=readAndWrite, args=(CURRENT_FILE_NAME,rectsArray,level,channel,processCounter,lock,total,));
			p.start();
				
	############################################ MultiThread   Test ############################################			
	elif MultiThread:
		print("###################### Mode MultiThread ######################");
		progressShow(0,0,total);
		LOCK = threading.Lock();
		def readAndWriteLocal(slide,writePath,rect,level,channel,lock):
				targetImage = slide.read_region((rect[0],rect[1]),level, (rect[2],rect[3]),channel);
				cv.imwrite(writePath,targetImage);
				del targetImage;
				global PROCESS_COUNT;
				lock.acquire();
				PROCESS_COUNT += 1;
				progressShow(PROCESS_COUNT,time.time()-time0,total);
				lock.release();
		for y in range(0,rows):
			for x in range(0,columns):
				width = height = pieceSize;
				if (x+1)*pieceSize>rangeWidth:
					width = rangeWidth- x*pieceSize;
				if (y+1)*pieceSize>rangeHeight:
					height = rangeHeight- y*pieceSize;
				x_1 = startX+x*pieceSize;
				y_1 = startY+y*pieceSize;
				realPos = getStartPos(bestSize,targetSize,x_1,y_1);
				path = os.path.join(outputPath,'_c%d_lv_%d_row_%d_clo_%d%s'%(channel,level,y,x,outputFormat));
				rect = (realPos[0],realPos[1],width,height);
				newThread = threading.Thread(target=readAndWriteLocal,args=(slide,path,rect,level,channel,LOCK,));
				newThread.setDaemon(True);
				newThread.start();
	############################################ Multiprocessing   Over ############################################
	else:
		print("###################### Mode Normal ######################");
		progressShow(0,0,total);
		for y in range(0,rows):
			for x in range(0,columns):
				width = height = pieceSize;
				if (x+1)*pieceSize>rangeWidth:
					width = rangeWidth- x*pieceSize;
				if (y+1)*pieceSize>rangeHeight:
					height = rangeHeight- y*pieceSize;
				x_1 = startX+x*pieceSize;
				y_1 = startY+y*pieceSize;
				realPos = getStartPos(bestSize,targetSize,x_1,y_1);
				# print("x_1 %d y_1 %d width %d height %d"%(x_1,y_1,width,height));
				targetImage = slide.read_region((realPos[0],realPos[1]),level, (width,height),channel);
				cv.imwrite(os.path.join(outputPath,'_c%d_lv_%d_row_%d_clo_%d%s'%(channel,level,y,x,outputFormat)),targetImage);
				percent = progressShow((y)*columns+(x+1),time.time()-time0,total);
				# print("Outputing image %d/%d time used %ds"%((y)*columns+(x+1),rows*columns,(time.time()-time0)));
				del targetImage;
	
	if MultiThread:
		
		while PROCESS_COUNT < total:
			time.sleep(0.5);
	if MultiProcess:
		
		while processCounter.value < total:
			time.sleep(0.5);
	sys.stdout.write("\r\n");# go back to the start of the next output line
	sys.stdout.flush();
	return (time.time()-time0);

class pasareWindowHandle(object):
	"""docstring for pasareWindowHandle"""
	def __init__(self):
		super(pasareWindowHandle, self).__init__()	
		self.root_ = tk.Tk();
		self.root_.resizable(width=False, height=False);
		self.root_.title("Pasare Aprieo svs file");
		self.root_.geometry("800x480");
		l = tk.Label(self.root_, text="This is a software with .svs file input output with images.", font=("Arial",12), width=800, height=1);
		l.pack(side=tk.TOP,pady=5);
		self.openFileBtn_ = tk.Button(self.root_, text="Open File", command=lambda:self.selectInputFile());
		self.openFileBtn_.pack(pady=5);
		self.openFileNameStr_ = tk.Variable();
		self.openFileNameStr_.set("openFileName");
		self.openFileName_ = tk.Entry(self.root_, textvariable=self.openFileNameStr_,width = 70,font=("Arial",12)).pack();
		
		self.outPutDirBtn_ = tk.Button(self.root_, text="Output Dir", command=self.selectOutputDir);
		self.outPutDirBtn_.pack(pady=5);

		self.outPutFolderStr_ = tk.Variable();
		self.outPutFolderStr_.set("output folder name");
		self.outPutFolder_ = tk.Entry(self.root_, textvariable=self.outPutFolderStr_,width = 70,font=("Arial",12)).pack();

		self.startAnalyzeBtn_ = tk.Button(self.root_, text="Analyze",width=10,height=1,command=lambda:self.startAnalyze());
		self.startAnalyzeBtn_.place(x=320,y=180,anchor=tk.CENTER);
		self.startAnalyzeBtn_['state']=tk.DISABLED;

		self.resetBtn_ = tk.Button(self.root_, text="Reset",width=10,height=1, command=lambda:self.onReset());
		self.resetBtn_.place(x=480,y=180,anchor=tk.CENTER);
		self.resetBtn_['state']=tk.DISABLED;

		self.canvaLineArray_ = [];
		self.thumbnailSize_ = None;

		self.selectRegionMode_ = False;
		self.IsOnAddMode_ = False;
		self.IsEditable_ = False;
		self.activeRect_ = None;
		self.selectedRegions_ = []; #the (startx,starty,endx,endy)'s set saved the rect des inside
		self.selectedRects_ = []; #the id set for those rects drawed on the canvas
		self.canvaLineGroup_ = {}; # for each selected rect on the thumbnil, saves the lines' id which are drawed inside the rect

		self.root_.mainloop();
	###################################################    UI RESPONSE     ########################################################
	###########################################    BUTTON & ComboboxSelected     ########################################################
	def selectInputFile(self):
		filename = filedialog.askopenfilename();
		if filename != '':
			self.openFileNameStr_.set(filename);
			self.startAnalyzeBtn_['state']=tk.NORMAL;
		else:
			self.openFileNameStr_.set("No File Chosed!");
			self.startAnalyzeBtn_['state']=tk.DISABLED;

	def selectOutputDir(self):
		dirName = filedialog.askdirectory();
		if dirName != '':
			self.outPutFolderStr_.set(dirName);
		else:
			self.outPutFolderStr_.set(os.path.abspath(os.curdir));

	def onSizeChange(self,eventObject):
		if self.selectRegionMode_:
			if len(self.selectedRegions_)>0:
				for regionRect in self.selectedRegions_:
					temp = tuple(eval(regionRect));
					self.drawLinesInRegion(temp);
		else:
			self.clearLinesAndRects();
			self.drawLinesInRegion();

	def onRangeItemSelected(self,eventObject):
		print("onRangeItemSelected "+self.rangeChosen_.get());

	def onAddNewRegion(self):
		self.IsOnAddMode_ = not self.IsOnAddMode_;
		if self.addNewRegionBtn_['text'] == "Add Region":
			self.addNewRegionBtn_['text']="cancle";
		else:
			self.addNewRegionBtn_['text']="Add Region";

	def onDeleteRegion(self):
		targetIndex = -1;
		for i, val in enumerate(self.selectedRegions_):
			if val == self.rangeChosen_.get():
				targetIndex = i;
		if targetIndex >= 0:
			targetRectId = self.selectedRects_[targetIndex];
			self.canvas_.delete(targetRectId);
			regionRect = self.selectedRegions_[targetIndex];
			linesArray = self.canvaLineGroup_[str(regionRect)];
			if linesArray != None and len(linesArray) > 0:
				for lineId in linesArray:
					self.canvas_.delete(lineId);
			del self.canvaLineGroup_[str(regionRect)];
			del self.selectedRects_[targetIndex];
			del self.selectedRegions_[targetIndex];
			self.rangeChosen_['values'] = self.selectedRegions_;
			if len(self.selectedRegions_)>0:
				self.rangeChosen_.current(len(self.selectedRegions_)-1);
			else:
				self.newRegion_="";
				self.rangeChosen_.set('');
				self.selectedRegions_
				self.redoBtn_['state'] = tk.DISABLED;
				self.startOutputBtn_['state']=tk.DISABLED;
	def onChangeOutputType(self,eventObject):
		if self.selectRegionMode_:
			if self.outputType_.get() == "By Range":
				return ;
			else:
				self.selectRegionMode_ = False;
				self.IsOnAddMode_ = False;
				self.addNewRegionBtn_['text']="Add Region"
				# hide add 'new region' btn and 'delete' btn
				# clear the rects and lines drawed on the Canvas
				self.addNewRegionBtn_['state']=tk.DISABLED;
				self.redoBtn_['state']=tk.DISABLED;
				self.rangeChosen_['state']=tk.DISABLED;
				self.startOutputBtn_['state']=tk.NORMAL;

				self.clearLinesAndRects();
				self.newRegion_="";  # UI clear
				self.rangeChosen_['values'] = self.selectedRegions_; # UI clear
				self.drawLinesInRegion();
		else:
			if self.outputType_.get() == "By Piece":
				return;
			else:
				self.selectRegionMode_ = True;
				# reshow add 'new region' btn and 'delete' btn
				self.addNewRegionBtn_['state']=tk.NORMAL;
				self.redoBtn_['state']=tk.NORMAL;
				self.rangeChosen_['state']=tk.NORMAL;
				self.startOutputBtn_['state']=tk.DISABLED;
				self.clearLinesAndRects();
	def onChangeProcess(self,cores):
		global CORES;
		CORES = int(cores);
	###################################################    TOUCH EVENT     ########################################################
	def onClickInThumbnil(self,event):
		if not self.IsOnAddMode_:
			return;
		self.activeRect_ = self.canvas_.create_rectangle(event.x,event.y,event.x+1,event.y+1,outline='green',width = 1);

	def onChangeRegion(self,event):
		if not self.IsOnAddMode_:
			return;
		startx,starty,endx,endy = self.canvas_.coords(self.activeRect_);
		self.canvasWidth_ = 300.0;
		self.canvasHeight_
		endX = event.x;
		endY = event.y;
		if endX>self.canvasWidth_:
			endX = self.canvasWidth_
		if endY>self.canvasHeight_:
			endY = self.canvasHeight_
		self.canvas_.coords(self.activeRect_,(startx, starty, endX, endY));

	def onClickFinished(self,event):
		if not self.IsOnAddMode_:
			return;
		startx,starty,endx,endy = self.canvas_.coords(self.activeRect_);
		regionItem = (startx,starty,endx,endy);
		self.selectedRects_.append(self.activeRect_);
		self.selectedRegions_.append(str(regionItem));
		self.canvaLineGroup_[str(regionItem)] = [];
		self.rangeChosen_['values'] = self.selectedRegions_;
		self.rangeChosen_.current(len(self.selectedRegions_)-1);
		self.activeRect_ = None;
		self.redoBtn_['state']=tk.NORMAL;
		self.addNewRegionBtn_['text']="Add Region";
		self.IsOnAddMode_ = False;
		self.drawLinesInRegion(regionItem);
		if len(self.selectedRegions_)>0:
			self.startOutputBtn_['state']=tk.NORMAL;
		else:
			self.startOutputBtn_['state']=tk.DISABLED;

	def startOutput(self,slide):
		self.outPutDirBtn_['state']=tk.DISABLED;
		self.openFileBtn_['state']=tk.DISABLED;
		self.startAnalyzeBtn_['state']=tk.DISABLED;
		self.resetBtn_['state']=tk.DISABLED;
		self.startOutputBtn_['state']=tk.DISABLED;
		self.addNewRegionBtn_['state']=tk.DISABLED;
		self.redoBtn_['state']=tk.DISABLED;

		if self.outPutFolderStr_.get() == "output folder name":
			result = messagebox.askquestion(title='Select The Output Folder', message='If not selected the output file will do to basic directory!  '+os.path.abspath(os.curdir));
			if result == 'yes':
				self.outPutFolderStr_.set(os.path.abspath(os.curdir));
			else:
				dirName = filedialog.askdirectory();
				if dirName != '':
					self.outPutFolderStr_.set(dirName);
				else:
					self.outPutFolderStr_.set(os.path.abspath(os.curdir));
		level = 0;
		resolution = self.resolutionChosen_.get().split(" ");
		width = int(resolution[0]);
		height = int(resolution[1]);
		for index in range(0,len(self.resolutionChosen_["values"])):
			if width == self.resolutionChosen_["values"][index][0] and height == self.resolutionChosen_["values"][index][1]:
				level = index;
		resol = (width,height);
		channel = int(self.outputChannleChosen_.get()[0]);
		fileName = os.path.basename(self.openFileNameStr_.get()).split('.')[0];
		outputFolderName = os.path.join(self.outPutFolderStr_.get(),fileName);
		outputFormat = self.outputFormatChosen_.get();
		pieceSize = int(self.pieceSizeChosen_.get());
		outputType = self.outputType_.get();
		rectArray = [];
		if outputType == "By Piece":
			rectArray.append((0,0,resol[0],resol[1]));
		else: # by Range
			for rect in self.selectedRegions_:
				temp = tuple(eval(rect));
				rectArray.append(getRealRectForOutput(resol,temp,self.thumbnailSize_));
		subfolders = initOutputFolder(outputFolderName,outputType,level,rectArray,channel,pieceSize);
		outputThumbnail(slide,outputFolderName,channel);
		print(">>>>>>>>>>>>>>   Output Folders:   >>>>>>>>>>>>>>");
		for folder in subfolders:
			print(folder);
		result = messagebox.askyesno("Tips","PLEASE WAIT UNTILL SUCCESS MESSAGE.Output Folder: %s"%(str(subfolders)));
		if result == True:
			print("######################## Start Output ########################");
			time0 = time.time();
			timeCost = 0.0;
			for i in range(len(rectArray)):
				if len(rectArray)>1:
					print("######################## Process Region %d ########################"%(i+1));
				rect = rectArray[i];
				subFolderPath = subfolders[i];
				timeCost += outputImageByRange(slide,level,channel,outputFormat,subFolderPath,rect,pieceSize);
			print("######################### End Output #########################");
			print("total time used %d"%(time.time()-time0));
			messagebox.showinfo("Tips",'PROCESS SUCCESS!!!\nUSING TIME %d SECONDS '%(timeCost));
		else:
			# delete subfolders
			for folder in subfolders:
				os.rmdir(folder);
			
			
		self.outPutDirBtn_['state']=tk.NORMAL;
		self.openFileBtn_['state']=tk.NORMAL;
		self.startAnalyzeBtn_['state']=tk.NORMAL;
		self.resetBtn_['state']=tk.NORMAL;
		self.openFileBtn_['state']=tk.NORMAL;
		self.startOutputBtn_['state']=tk.NORMAL;

		if len(self.selectedRegions_)>0:
			self.redoBtn_['state']=tk.NORMAL;
		else:
			self.redoBtn_['state']=tk.DISABLED;
		if outputType == "By Range":
			self.addNewRegionBtn_['state']=tk.NORMAL;
	def onReset(self):
		self.openFileNameStr_.set("openFileName");
		self.outPutFolderStr_.set("output folder name");
		self.startAnalyzeBtn_['state']=tk.DISABLED;
		self.resetBtn_['state']=tk.DISABLED;
		self.IsOnAddMode_ = False;
		self.IsEditable_ = False;
		self.activeRect_ = None;
		global PythonVersion;
		if PythonVersion == 2:
			del self.selectedRegions_[:];
			del self.selectedRects_[:];
		else:
			self.selectedRegions_.clear();
			self.selectedRects_.clear();
		self.canvaLineGroup_.clear();	

		self.canvas_.delete("all");
		self.canvaLineArray_ = [];
		# self.typeCanvas_.delete("all");

		if hasattr(self,'thumbnail_'):
			self.thumbnail_.destroy();
			delattr(self,'thumbnail_');
		if hasattr(self,'rootFrame_'):
			self.rootFrame_.destroy();
			delattr(self,'rootFrame_');
		if hasattr(self,'canvas_'):
			self.canvas_.destroy();
			delattr(self,'canvas_');
	###################################################    UI RESPONSE     ########################################################	
	def clearLinesAndRects(self):
		for regionRect,linesArray in self.canvaLineGroup_.items():
			if linesArray != None and len(linesArray) > 0:
				for lineId in linesArray:
					self.canvas_.delete(lineId);		
		for rectId in self.selectedRects_:
			self.canvas_.delete(rectId);
		global PythonVersion;
		if PythonVersion == 2:
			del self.selectedRegions_[:];
			del self.selectedRects_[:];
		else:
			self.selectedRegions_.clear();
			self.selectedRects_.clear();
		self.canvaLineGroup_.clear();
	                       #############################    UTILITY    #############################	
	def warningBox(self,messageInfo):
		messagebox.showwarning(title='WARNING', 
								  message=messageInfo);
	                       #############################    UTILITY    #############################				

	def drawLinesInRegion(self,targetRect=-1):
		if targetRect==-1:
			res = self.resolutionChosen_.get().split(" ");
			targetRect = [0,0,int(res[0]),int(res[1])];
		outputSize = self.resolutionChosen_.get().split(" ");
		pieceSize = int(self.pieceSizeChosen_.get());
		offset = self.thumbnailSize_[0]/int(outputSize[0])*pieceSize;

		columns = int(math.floor(int(targetRect[2]-targetRect[0])/offset));
		rows = int(math.floor(int(targetRect[3]-targetRect[1])/offset));
		if (str(targetRect) in self.canvaLineGroup_) and len(self.canvaLineGroup_[str(targetRect)]) > 0:
			for itemId in self.canvaLineGroup_[str(targetRect)]:
				self.canvas_.delete(itemId);
		else:
			self.canvaLineGroup_[str(targetRect)] = [];

		for x in range(columns):
			lineId = self.canvas_.create_line(targetRect[0]+(x+1)*offset,targetRect[1],targetRect[0]+(x+1)*offset,targetRect[3],fill='red');
			self.canvaLineGroup_[str(targetRect)].append(lineId);
		for y in range(rows):
			lineId = self.canvas_.create_line(targetRect[0],targetRect[1]+(y+1)*offset,targetRect[2],targetRect[1]+(y+1)*offset,fill='blue');
			self.canvaLineGroup_[str(targetRect)].append(lineId);

	def startAnalyze(self):
		self.openFileBtn_['state']=tk.DISABLED;
		self.startAnalyzeBtn_['state']=tk.DISABLED;
		self.clearLinesAndRects();
		fileName = self.openFileNameStr_.get();
		filePrex = fileName.split('.')[1];
		
		if filePrex.lower() == 'tiff' or filePrex.lower() == 'svs':
			slide = openslide.OpenSlide(fileName);
			global CURRENT_FILE_NAME;
			CURRENT_FILE_NAME = fileName;
			
			bestResolution = slide.level_dimensions[0];
			self.canvasWidth_ = 300.0;
			self.canvasHeight_ = math.floor((self.canvasWidth_/bestResolution[0])*bestResolution[1]);
			size = self.thumbnailSize_ = (self.canvasWidth_,self.canvasHeight_);

			slide_thumbnail = slide.get_thumbnail(size);
			from PIL import Image, ImageTk
			self.render_= ImageTk.PhotoImage(slide_thumbnail);
			if hasattr(self,'thumbnail_'):
				self.thumbnail_.destroy();
				delattr(self,'thumbnail_');
			self.thumbnail_ = tk.Label(self.root_,image=self.render_);
			self.thumbnail_.image = self.render_;
			self.thumbnail_.place(x=470,y=230);

			if hasattr(self,'rootFrame_'):
				self.rootFrame_.destroy();
				delattr(self,'rootFrame_');
			self.rootFrame_ = tk.Frame(self.root_,width=500,height=400);##bg='blue'
			self.rootFrame_.place(x=20,y=200,anchor=tk.NW);


			from PIL import Image, ImageTk
			self.canvas_ = Canvas(self.root_, width=self.canvasWidth_,height=self.canvasHeight_);
			self.canvas_.place(x=470,y=230);
			self.canvas_.create_image(self.canvasWidth_/2,self.canvasHeight_/2,anchor=tk.CENTER,image=self.render_);
			self.canvas_.bind("<Button-1>", self.onClickInThumbnil);
			self.canvas_.bind("<B1-Motion>", self.onChangeRegion);
			self.canvas_.bind("<ButtonRelease-1>", self.onClickFinished);
        
			choseResolutionLabel = tk.Label(self.rootFrame_, text="Choose the output Resolution", font=("Arial",12), width=25, height=1);
			choseResolutionLabel.place(x=120,y=20,anchor=tk.CENTER);

			self.resolutions_ = tk.StringVar().set(slide.level_dimensions[0]);
			self.resolutionChosen_ = ttk.Combobox(self.rootFrame_, width=20, textvariable=self.resolutions_, state="readonly");#,command= lambda:self.onSizeChange()
			self.resolutionChosen_["values"] = slide.level_dimensions;
			# DEFAULT OUOUT RESOLUTION IS THE BEST RESOLUTION
			self.resolutionChosen_.current(0);
			self.resolutionChosen_.place(x=120,y=50,anchor=tk.CENTER);
			self.resolutionChosen_.bind("<<ComboboxSelected>>",self.onSizeChange);

			outputTypeLabel = tk.Label(self.rootFrame_, text="Choose output type", font=("Arial",12), width=25, height=1);
			outputTypeLabel.place(x=350,y=20,anchor=tk.CENTER);
			self.outputType_ = tk.StringVar();
			self.outputType_ = ttk.Combobox(self.rootFrame_, width=20, textvariable=self.outputType_, state="readonly");
			self.outputType_["values"] = ("By Piece","By Range");

			defaultResl = slide.level_dimensions[0];
			if outputModeClassifier(defaultResl) == "RangeMode":
				self.selectRegionMode_ = True;
				self.outputType_.current(1);

				self.addNewRegionBtn_ = tk.Button(self.rootFrame_, text="Add Region",width=10, command=lambda:self.onAddNewRegion());
				self.addNewRegionBtn_.place(x=310,y=140,anchor=tk.CENTER);
				self.redoBtn_ = tk.Button(self.rootFrame_, text="Delete", command=lambda:self.onDeleteRegion());
				self.redoBtn_.place(x=400,y=140,anchor=tk.CENTER);
				self.redoBtn_['state']=tk.DISABLED;# active, disabled, or normal

				self.newRegion_ = tk.StringVar();
				self.rangeChosen_ = ttk.Combobox(self.rootFrame_, width=20, textvariable=self.newRegion_, state="readonly");
				self.rangeChosen_["values"] = self.selectedRegions_;
				self.rangeChosen_.place(x=350,y=170,anchor=tk.CENTER);
				self.rangeChosen_.bind("<<ComboboxSelected>>",self.onRangeItemSelected);
			else:
				self.outputType_.current(0);
				self.selectRegionMode_ = False;

			self.outputType_.place(x=350,y=50,anchor=tk.CENTER);
			self.outputType_.bind("<<ComboboxSelected>>",self.onChangeOutputType);

			pieceSizeLabel = tk.Label(self.rootFrame_, text="Choose piece size", font=("Arial",12), width=25, height=1);
			pieceSizeLabel.place(x=350,y=80,anchor=tk.CENTER);
			self.pieceSize_ = tk.StringVar();
			self.pieceSizeChosen_ = ttk.Combobox(self.rootFrame_, width=20, textvariable=self.pieceSize_, state="readonly");
			self.pieceSizeChosen_["values"] = ("1000","3000","5000","10000");
			self.pieceSizeChosen_.current(3);
			self.pieceSizeChosen_.place(x=350,y=110,anchor=tk.CENTER);
			self.pieceSizeChosen_.bind("<<ComboboxSelected>>",self.onSizeChange);

			choseFormatLabel = tk.Label(self.rootFrame_, text="Choose the output Fromat", font=("Arial",12), width=25, height=1);
			choseFormatLabel.place(x=120,y=80,anchor=tk.CENTER);
			self.outputFormat_ = tk.StringVar().set(".png");
			self.outputFormatChosen_ = ttk.Combobox(self.rootFrame_, width=20, textvariable=self.outputFormat_, state="readonly");
			self.outputFormatChosen_["values"] = (".png",".jpeg",".bmp");
			self.outputFormatChosen_.current(0);
			self.outputFormatChosen_.place(x=120,y=110,anchor=tk.CENTER);

			choseChannelLabel = tk.Label(self.rootFrame_, text="Choose the output Channel", font=("Arial",12), width=25, height=1);
			choseChannelLabel.place(x=120,y=140,anchor=tk.CENTER);
			self.outputChannel_ = tk.StringVar().set("3:RGB");
			self.outputChannleChosen_ = ttk.Combobox(self.rootFrame_, width=20, textvariable=self.outputChannel_, state="readonly");
			self.outputChannleChosen_["values"] = ("1:gray","3:RGB","4:RGBA");
			self.outputChannleChosen_.current(1);
			self.outputChannleChosen_.place(x=120,y=170,anchor=tk.CENTER);

			self.multiProcess_ = Checkbutton(self.rootFrame_,text ='Multi Cores?',command=isMultiProcess);
			self.multiProcess_.place(x=30,y=210,anchor=tk.W);

			length = (multiprocessing.cpu_count()-2)*30;
			if length > 100:
				length = 100;
			scale = tk.Scale(self.rootFrame_,
							 from_=1, 
							 to=multiprocessing.cpu_count()-2,
							 length=length, 
							 orient=tk.HORIZONTAL,
							 command=self.onChangeProcess);
			scale.set(2); # 设置初始值
			scale.place(x=140,y=204,anchor=tk.W);

			self.multiThread_ = Checkbutton(self.rootFrame_,text ='Multi Threads',command=isMultiThread);
			self.multiThread_.place(x=30,y=230,anchor=tk.W);
			self.resetBtn_['state']=tk.NORMAL;

			self.startOutputBtn_ = tk.Button(self.rootFrame_, text="Output",command=lambda:self.startOutput(slide));
			self.startOutputBtn_.place(x=350,y=220,anchor=tk.CENTER);
			self.openFileBtn_['state']=tk.NORMAL;

			if self.selectRegionMode_:
				self.startOutputBtn_['state']=tk.DISABLED;
		else:
			messagebox.showinfo('SUPPORT .svs FILE AND .tiff FILE ONLY');
			self.openFileBtn_['state']=tk.NORMAL;
			return False;
if __name__ == "__main__":
	# print("cpu_count is %d "%(multiprocessing.cpu_count()));
	newWindow = pasareWindowHandle();
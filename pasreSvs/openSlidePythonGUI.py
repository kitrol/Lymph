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

def initMutiChannelImage(slide,level,resolution,outputFormat):
	# default muti channel for 3 channels
	maxSize = 40000;
	threshold = 5000;
	channel=4;
	if (resolution[0] > maxSize) or (resolution[1] > maxSize):  ## image is too big to analyse
		rows = int(math.ceil(resolution[0]/threshold));
		columns = int(math.ceil(resolution[1]/threshold));
		targetImage = np.zeros([resolution[1],resolution[0],channel],dtype=np.uint8);
		for x in range(0,rows):
			for y in range(0,columns):
				width = height = threshold;
				if (x+1)*threshold>resolution[0]:
					width = resolution[0]- x*threshold;
				if (y+1)*threshold>resolution[1]:
					height = resolution[1]- y*threshold;
				imagePiece = slide.read_region((x*threshold,y*threshold),level, (width,height),channel);
				targetImage[y*threshold:y*threshold+height,x*threshold:x*threshold+width,:] = imagePiece;
		return targetImage;
	else:
		targetImage = slide.read_region((0,0),level, resolution,channel);
		return targetImage;

def initPieceOutputDir(outputFullPathAndName,level,channel,isByPiece,pieceSize):
	targetPieceDir = outputFullPathAndName;
	if isByPiece:
		targetPieceDir = (targetPieceDir+"_lv%d_pieceSize=%d_Channel_%d"%(level,pieceSize,channel));
		targetPieceDir = targetPieceDir+"\\";
		if platform.system() == 'Darwin' or platform.system() == 'Linux':
			targetPieceDir = targetPieceDir+"/";
		if os.path.exists(targetPieceDir):
			for f in os.listdir(targetPieceDir):
				filePath = os.path.join(targetPieceDir,f);
				if os.path.isfile(filePath):	
					os.remove(filePath);
		else:
			os.mkdir(targetPieceDir);
	return targetPieceDir;

def outputImageByPiece(sourceImage,pieceSize,channel,level,outputFormat,outputDir):
	resolution = sourceImage.shape;
	rows = int(math.ceil(resolution[0]/pieceSize));
	columns = int(math.ceil(resolution[1]/pieceSize));
	pieceDetailFile(outputDir,resolution[0],resolution[1],pieceSize,rows,columns);
	imagePiece = np.zeros([pieceSize,pieceSize,channel],dtype=np.uint8);
	for x in range(0,rows):
		for y in range(0,columns):
			width = height = pieceSize;
			if (x+1)*pieceSize>resolution[0]:
				width = resolution[0]- x*pieceSize;
			if (y+1)*pieceSize>resolution[1]:
				height = resolution[1]- y*pieceSize;
			if channel == 1:
				imagePiece = sourceImage[x*pieceSize:x*pieceSize+width,y*pieceSize:y*pieceSize+height];
			else:
				imagePiece = sourceImage[x*pieceSize:x*pieceSize+width,y*pieceSize:y*pieceSize+height,:];
			cv.imwrite(outputDir+'_c%d_lv_%d_row_%d_clo_%d%s'%(channel,level,x,y,outputFormat),imagePiece);

def pieceDetailFile(outputDir,width,height,pieceSize,rows,columns):
	file = open(outputDir+"des", "w+");
	string = 'width:%d\nheight:%d\npieceSize:%s\rrows:%d\ncolumns:%d'%(width,height,str(pieceSize),rows,columns);
	file.write(string);
	file.close();
			
def outputImage(slide,level,resolution,channel,outputFormat,outputFullPathAndName,isByPiece=False,pieceSize=0):##needWriteToDisk=True
	time0 = time.time();
	if (pieceSize == 0) or (not isByPiece):
		pieceSize = 3000;

	pieceDir = initPieceOutputDir(outputFullPathAndName,level,channel,isByPiece,pieceSize);
	mutiChannelImage = initMutiChannelImage(slide,level,resolution,outputFormat);
	targetImage = mutiChannelImage;
	if channel == 1:
		singleChannelImage = cv.cvtColor(mutiChannelImage, cv.COLOR_BGR2GRAY);
		targetImage = singleChannelImage;
	elif channel == 3:
		targetImage = mutiChannelImage[:,:,:3];
		
	cv.imwrite(outputFullPathAndName+'_c%d_lv_%d%s'%(channel,level,outputFormat),targetImage);
	if isByPiece:
		outputImageByPiece(targetImage,pieceSize,channel,level,outputFormat,pieceDir);
	
	return (time.time()-time0);

def outputImageByRange(slide,level,resolution,channel,outputFormat,outputFullPathAndName,rangeSize):
	time0 = time.time();
	# rangeSize:[startX startY width height]
	resolution = (rangeSize[2],rangeSize[3]);
	# if :
	# 	pass
	# rows = int(math.ceil(resolution[0]/pieceSize));
	# columns = int(math.ceil(resolution[1]/pieceSize));
	# pieceDetailFile(outputDir,resolution[0],resolution[1],pieceSize,rows,columns);
	# imagePiece = np.zeros([pieceSize,pieceSize,channel],dtype=np.uint8);
	# for x in range(0,rows):
	# 	for y in range(0,columns):
	# 		width = height = pieceSize;
	# 		if (x+1)*pieceSize>resolution[0]:
	# 			width = resolution[0]- x*pieceSize;
	# 		if (y+1)*pieceSize>resolution[1]:
	# 			height = resolution[1]- y*pieceSize;
	# 		if channel == 1:
	# 			imagePiece = sourceImage[x*pieceSize:x*pieceSize+width,y*pieceSize:y*pieceSize+height];
	# 		else:
	# 			imagePiece = sourceImage[x*pieceSize:x*pieceSize+width,y*pieceSize:y*pieceSize+height,:];
	# 		cv.imwrite(outputDir+'_c%d_lv_%d_row_%d_clo_%d%s'%(channel,level,x,y,outputFormat),imagePiece);

	targetImage = slide.read_region((rangeSize[0],rangeSize[1]),level, resolution,channel);
	cv.imwrite(outputDir+'_lv_%d_w_%d_h_%d%s'%(level,rangeSize[2],rangeSize[3],outputFormat),targetImage);
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

		self.resetBtn_ = tk.Button(self.root_, text="Reset",width=10,height=1, command=lambda:self.reset());
		self.resetBtn_.place(x=480,y=180,anchor=tk.CENTER);
		self.resetBtn_['state']=tk.DISABLED;

		self.isByPiece_ = False;
		self.canvaLineArray_ = [];
		self.thumbnailSize_ = None;

		self.root_.mainloop();
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
		self.drawLines();

	def onIsByPieceCheck(self):
		self.isByPiece_ = not self.isByPiece_;

	def warningBox(self,messageInfo):
		messagebox.showwarning(title='WARNING', 
								  message=messageInfo);

	def startOutput(self,slide):
		self.outPutDirBtn_['state']=tk.DISABLED;
		self.openFileBtn_['state']=tk.DISABLED;
		self.startAnalyzeBtn_['state']=tk.DISABLED;
		self.resetBtn_['state']=tk.DISABLED;
		self.startOutputBtn_['state']=tk.DISABLED;

		# print(self.resolutionChosen_.get());
		# print(self.outputFormatChosen_.get());
		# print(self.outPutFolderStr_.get());
		# print(self.resolutionChosen_.get());
		# print(self.resolutionChosen_["values"]);
		# print(self.outputChannleChosen_.get());
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
		outputName = self.outPutFolderStr_.get()+"\\"+fileName;
		if platform.system() == 'Darwin' or platform.system() == 'Linux':
			outputName = self.outPutFolderStr_.get()+"/"+fileName;
		outputFormat = self.outputFormatChosen_.get();
		pieceSize = int(self.pieceSizeChosen_.get());
		self.warningBox('PLEASE WAIT UNTILL SUCCESS MESSAGE');
		# timeCost = outputImage(slide,level,resol,channel,outputFormat,outputName,isByPiece=True,pieceSize=pieceSize);#self.isByPiece_
		rangeSize = (12000,20000,70000,32000);
		timeCost = outputImageByRange(slide,level,resol,channel,outputFormat,outputName,rangeSize);
		self.warningBox('PROCESS SUCCESS!!!\nUSING TIME %d SECONDS '%(timeCost));

		self.outPutDirBtn_['state']=tk.NORMAL;
		self.openFileBtn_['state']=tk.NORMAL;
		self.startAnalyzeBtn_['state']=tk.NORMAL;
		self.resetBtn_['state']=tk.NORMAL;
		self.openFileBtn_['state']=tk.NORMAL;
		self.startOutputBtn_['state']=tk.NORMAL;
		
	def reset(self):
		self.openFileNameStr_.set("openFileName");
		self.outPutFolderStr_.set("output folder name");
		self.startAnalyzeBtn_['state']=tk.DISABLED;
		self.resetBtn_['state']=tk.DISABLED;
		self.canvas_.delete("all");
		self.canvaLineArray_ = [];

		if hasattr(self,'thumbnail_'):
			self.thumbnail_.destroy();
			delattr(self,'thumbnail_');
		if hasattr(self,'rootFrame_'):
			self.rootFrame_.destroy();
			delattr(self,'rootFrame_');
		if hasattr(self,'canvas_'):

			self.canvas_.destroy();
			delattr(self,'canvas_');
			
	def drawLines(self):
		outputSize = self.resolutionChosen_.get().split(" ");
		pieceSize = int(self.pieceSizeChosen_.get());
		rows = int(math.floor(int(outputSize[0])/pieceSize));
		columns = int(math.floor(int(outputSize[1])/pieceSize));
		offset = self.thumbnailSize_[0]/int(outputSize[0])*pieceSize;
		for itemId in self.canvaLineArray_:
			self.canvas_.delete(itemId);
		for x in range(rows):
			lineId = self.canvas_.create_line((x+1)*offset,0,(x+1)*offset,self.thumbnailSize_[1],fill='red');
			self.canvaLineArray_.append(lineId);
		for y in range(columns):
			lineId = self.canvas_.create_line(0,(y+1)*offset,self.thumbnailSize_[0],(y+1)*offset,fill='blue');
			self.canvaLineArray_.append(lineId);

	def startAnalyze(self):
		self.openFileBtn_['state']=tk.DISABLED;
		self.startAnalyzeBtn_['state']=tk.DISABLED;

		fileName = self.openFileNameStr_.get();
		filePrex = fileName.split('.')[1];
		
		if filePrex.lower() == 'tiff' or filePrex.lower() == 'svs':
			slide = openslide.OpenSlide(fileName);
			
			bestResolution = slide.level_dimensions[0];
			maxWidth = 300.0;
			height = math.floor((maxWidth/bestResolution[0])*bestResolution[1]);
			size = self.thumbnailSize_ = (maxWidth,height);

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
			self.canvas_ = Canvas(self.root_, width=maxWidth,height=height);
			self.canvas_.place(x=470,y=230);
			self.canvas_.create_image(maxWidth/2,height/2,anchor=tk.CENTER,image=self.render_);
			# self.canvas.create_line(0,100,200,100,fill='red');
			
        
			choseResolutionLabel = tk.Label(self.rootFrame_, text="Choose the output Resolution", font=("Arial",12), width=25, height=1);
			choseResolutionLabel.place(x=120,y=20,anchor=tk.CENTER);

			self.resolutions_ = tk.StringVar().set(slide.level_dimensions[0]);
			self.resolutionChosen_ = ttk.Combobox(self.rootFrame_, width=20, textvariable=self.resolutions_, state="readonly");#,command= lambda:self.onSizeChange()
			self.resolutionChosen_["values"] = slide.level_dimensions;
			self.resolutionChosen_.current(0);
			self.resolutionChosen_.place(x=120,y=50,anchor=tk.CENTER);
			self.resolutionChosen_.bind("<<ComboboxSelected>>",self.onSizeChange);

			self.isByPieceCheck_ = Checkbutton(self.rootFrame_,text ='output Piece?',command = lambda:self.onIsByPieceCheck());
			self.isByPieceCheck_.place(x=350,y=20,anchor=tk.CENTER);

			pieceSizeLabel = tk.Label(self.rootFrame_, text="Choose piece size", font=("Arial",12), width=25, height=1);
			pieceSizeLabel.place(x=350,y=50,anchor=tk.CENTER);

			self.pieceSize_ = tk.StringVar().set("500");
			self.pieceSizeChosen_ = ttk.Combobox(self.rootFrame_, width=20, textvariable=self.pieceSize_, state="readonly");
			self.pieceSizeChosen_["values"] = ("100","200","300","400","500","600","700","800","900","1000","3000","10000");
			self.pieceSizeChosen_.current(11);
			self.pieceSizeChosen_.place(x=350,y=80,anchor=tk.CENTER);
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

			self.startOutputBtn_ = tk.Button(self.rootFrame_, text="Output",command=lambda:self.startOutput(slide));
			self.startOutputBtn_.place(x=120,y=210,anchor=tk.CENTER);
			self.openFileBtn_['state']=tk.NORMAL;
			self.resetBtn_['state']=tk.NORMAL;

			self.drawLines();
		else:
			self.openFileBtn_['state']=tk.NORMAL;
			return False;

newWindow = pasareWindowHandle();



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
def outputPieceOfSlide(slide,outputBigImage=None,pieceFolder):
	pass
def outputImage(slide,level,resolution,channel,outputFormat,outputFullPathAndName,isByPiece=False,pieceSize=0,needWriteToDisk=True):
	time0 = time.time();
	threshold = int(pieceSize);
	pieceDir = outputFullPathAndName;
	if (threshold == 0) or (not isByPiece):
		threshold = 3000;
	maxSize = 20000;
	if channel == 1:
		timecost,threeChannelImage = outputImage(slide,level,resolution,3,outputFormat,outputFullPathAndName,isByPiece,False);
		gray = cv.cvtColor(threeChannelImage, cv.COLOR_BGR2GRAY);
		cv.imwrite(outputFullPathAndName+'_c%d_lv_%d%s'%(channel,level,outputFormat),gray);
		return (time.time()-time0),gray;
	else:
		if isByPiece:
			pieceDir = (pieceDir+"pieceSize=%d"%(threshold));
			if os.path.exists(pieceDir):
	 			shutil.rmtree(pieceDir,True);
			os.mkdir(pieceDir);
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
					if isByPiece and needWriteToDisk:
						cv.imwrite(pieceDir+'_c%d_lv_%d_row_%d_clo_%d%s'%(channel,level,x,y,outputFormat),imagePiece);
			if needWriteToDisk:
				cv.imwrite(outputFullPathAndName+'_c%d_lv_%d%s'%(channel,level,outputFormat),targetImage);
			return (time.time()-time0),targetImage;
		else:
			targetImage = slide.read_region((0,0),level, resolution,channel);
			if needWriteToDisk:
				cv.imwrite(outputFullPathAndName+'_c%d_lv_%d%s'%(channel,level,outputFormat),targetImage);
			return (time.time()-time0),targetImage;

class pasareWindowHandle(object):
	"""docstring for pasareWindowHandle"""
	def __init__(self):
		super(pasareWindowHandle, self).__init__()	
		self.root_ = tk.Tk();
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
		if platform.system() == 'Darwin':
			outputName = self.outPutFolderStr_.get()+"/"+fileName;
		outputFormat = self.outputFormatChosen_.get();
		pieceSize = self.pieceSizeChosen_.get();
		self.warningBox('PLEASE WAIT UNTILL SUCCESS MESSAGE');
		timeCost,imageItem = outputImage(slide,level,resol,channel,outputFormat,outputName,isByPiece=self.isByPiece_,pieceSize=pieceSize);
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

		if hasattr(self,'thumbnail_'):
			self.thumbnail_.destroy();
			delattr(self,'thumbnail_');
		if hasattr(self,'rootFrame_'):
			self.rootFrame_.destroy();
			delattr(self,'rootFrame_');
			

	def startAnalyze(self):
		self.openFileBtn_['state']=tk.DISABLED;
		self.startAnalyzeBtn_['state']=tk.DISABLED;

		fileName = self.openFileNameStr_.get();
		if fileName != '':
			filePrex = fileName[-4:];
			if filePrex.lower() == '.svs':
				slide = openslide.OpenSlide(fileName);
				bestResolution = slide.level_dimensions[0];
				maxWidth = 300.0;
				height = math.floor((maxWidth/bestResolution[0])*bestResolution[1]);
				size = (maxWidth,height);
				slide_thumbnail = slide.get_thumbnail(size);
				from PIL import Image, ImageTk
				render= ImageTk.PhotoImage(slide_thumbnail);
				if hasattr(self,'thumbnail_'):
					self.thumbnail_.destroy();
					delattr(self,'thumbnail_');
				self.thumbnail_ = tk.Label(self.root_,image=render);
				self.thumbnail_.image = render;
				self.thumbnail_.place(x=500,y=230);

				if hasattr(self,'rootFrame_'):
					self.rootFrame_.destroy();
					delattr(self,'rootFrame_');
				self.rootFrame_ = tk.Frame(self.root_,width=500,height=400);##bg='blue'
				self.rootFrame_.place(x=20,y=200,anchor=tk.NW);

				choseResolutionLabel = tk.Label(self.rootFrame_, text="Choose the output Resolution", font=("Arial",12), width=25, height=1);
				choseResolutionLabel.place(x=120,y=20,anchor=tk.CENTER);

				self.resolutions_ = tk.StringVar().set(slide.level_dimensions[0]);
				self.resolutionChosen_ = ttk.Combobox(self.rootFrame_, width=20, textvariable=self.resolutions_, state="readonly");
				self.resolutionChosen_["values"] = slide.level_dimensions;
				self.resolutionChosen_.current(0);
				self.resolutionChosen_.place(x=120,y=50,anchor=tk.CENTER);

				self.isByPieceCheck_ = Checkbutton(self.rootFrame_,text ='output Piece?',command = lambda:self.onIsByPieceCheck());
				self.isByPieceCheck_.place(x=350,y=20,anchor=tk.CENTER);
 
				pieceSizeLabel = tk.Label(self.rootFrame_, text="Choose piece size", font=("Arial",12), width=25, height=1);
				pieceSizeLabel.place(x=350,y=50,anchor=tk.CENTER);

				self.pieceSize_ = tk.StringVar().set("500");
				self.pieceSizeChosen_ = ttk.Combobox(self.rootFrame_, width=20, textvariable=self.pieceSize_, state="readonly");
				self.pieceSizeChosen_["values"] = ("100","200","300","400","500","600","700","800","900","1000","2000","3000");
				self.pieceSizeChosen_.current(4);
				self.pieceSizeChosen_.place(x=350,y=80,anchor=tk.CENTER);

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
			else:
				self.openFileBtn_['state']=tk.NORMAL;
				return False;
		else:
			self.openFileBtn_['state']=tk.NORMAL;
			return False;

newWindow = pasareWindowHandle();



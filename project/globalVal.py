import platform
import os


THRESHOLD = 27.0;
MAX_SIZE = 45;
MIN_RATIO = 0.5;
worktDir_ = '';
TrainFolder = '\\..\\..\\train_data\\';
TextFolder = '\\..\\..\\markedRegionsText\\';
newTestFolder = '\\..\\..\\newTestData\\';
outputFolder = '\\..\\..\\outputData\\';

def initDir(argv):
	global worktDir_;
	global TrainFolder;
	global TextFolder;
	global newTestFolder;
	global outputFolder;
	sysstr = platform.system();
	if sysstr == "Windows":
		pass;
	else:
		TrainFolder = '/../../train_data/';
		TextFolder = '/../../markedRegionsText/';
		newTestFolder = '/../../newTestData/' 
	worktDir_ = os.path.dirname(argv[0]);
	print("Working Dir is ",worktDir_);
	TrainFolder = worktDir_+TrainFolder;
	TextFolder  = worktDir_+TextFolder;
	newTestFolder= worktDir_+newTestFolder;
	outputFolder = worktDir_+outputFolder;

	os.chdir(TrainFolder);
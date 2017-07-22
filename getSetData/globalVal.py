import platform
import os


THRESHOLD = 4;
worktDir_ = '';
TrainFolder = '\\..\\..\\train_data';
TextFolder = '\\..\\..\\markedRegionsText\\';
newTestFolder = '\\..\\..\\newTestData\\';

def initDir(argv):
	global worktDir_;
	global TrainFolder;
	global TextFolder;
	sysstr = platform.system();
	if sysstr == "Windows":
		pass;
	else:
		TrainFolder = '/../../train_data';
		TextFolder = '/../../markedRegionsText/';
		newTestFolder = '/../../newTestData/' 
	worktDir_ = os.path.dirname(argv[0]);
	print("Working Dir is ",worktDir_);
	TrainFolder = worktDir_+TrainFolder;
	os.chdir(TrainFolder);
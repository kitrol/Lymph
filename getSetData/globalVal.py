import platform
import os



worktDir_ = '';
TrainFolder = '\\..\\..\\train_data';
TextFolder = '\\..\\..\\markedRegionsText\\';

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
	worktDir_ = os.path.dirname(argv[0]);
	print("Woring dir is ",worktDir_);
	TrainFolder = worktDir_+TrainFolder;
	os.chdir(TrainFolder);
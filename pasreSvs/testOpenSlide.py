import openslide
import numpy as np
import cv2 as cv
from PIL import Image

slide = openslide.OpenSlide('D:\Lymph_Follicle\CMU-1-JP2K-33005.svs');
print("detect_format "+slide.detect_format('D:\Lymph_Follicle\CMU-1-JP2K-33005.svs'));
print("slide dimensions is");
print(slide.dimensions);
print("slide level_dimensions is");
print(slide.level_dimensions);
print("slide level_downsamples is");
print(slide.level_downsamples);
print("slide get_best_level_for_sownsample is");
print(slide.get_best_level_for_downsample(3.0));
print("slide count is %d"%(slide.level_count));
level = 0;
# read_region(location, level, size)
targetImage = slide.read_region((0,0),level, slide.level_dimensions[level]);
# cv.imwrite('D:\Lymph_Follicle\CMU-1-JP2K-33005.png',targetImage);
targetImage.save('D:\Lymph_Follicle\CMU-1-JP2K-33005'+"_%d_%d"%(slide.level_dimensions[level][0],slide.level_dimensions[level][1])+'.png');
slide.close();
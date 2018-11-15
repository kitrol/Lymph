#!/usr/bin/python
# -*- coding: UTF-8 -*-
import multiprocessing
import time
import os

datalist=['+++']
# 我是
def adddata():
    global datalist
    datalist.append(1)
    datalist.append(2)
    datalist.append(3)
    print("sub process",os.getpid(),datalist);

if __name__=="__main__":
    p=multiprocessing.Process(target=adddata,args=())
    p.start()
    p.join()
    datalist.append("a")
    datalist.append("b")
    datalist.append("c") 
    print("main process",os.getpid(),datalist)

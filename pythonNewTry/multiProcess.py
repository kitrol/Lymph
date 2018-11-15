import multiprocessing
import time
testNUM = 0;
def worker(interval,lock):
    n = 5;
    while n > 0:
        print("The time is {0}".format(time.ctime()));
        time.sleep(interval);
        n -= 1;
        testNUM += 1; 
        print("testNUM is %d"%(testNUM));

if __name__ == "__main__":
    lock = multiprocessing.Lock();
    for x in range(0,2):
        p = multiprocessing.Process(target = worker, args = (1,lock));
        p.start();
        print("p.pid:", p.pid);
        print("p.name:", p.name);
        print("p.is_alive:", p.is_alive());

    
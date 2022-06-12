from calendar import c
from multiprocessing.sharedctypes import Value
from re import I
from textwrap import indent
import threading
from time import sleep
from timeit import default_timer as timer

job_list = []
partition_list = []
logs = []
error = []
jobType = False #false = first fit / true = best fit

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

class Partition:
    def __init__(self, id, size):
        self.id = id
        self.size = size
        self.time = int(0)
        self.busy = False
        self.job = None

    @threaded
    def startWork(self):
        while(self.time > 0):
            self.time -= 1
            sleep(1)

        self.busy = False
        self.job = None
        if not jobType:
            assignJobFirstFit()
        else:
            assignJobBestFit()


class Job:
    def __init__(self, id, size, time):
        self.id = id
        self.size = size
        self.time = int(time)

import os

def cls():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')
    
def readjobs(file):
    with open(file) as file:
        return list(tuple(x.replace("\n", "").split(" ")) for x in file.readlines()[1::])

def readpartitions(file):
    with open(file) as file:
        return list(tuple(x.replace("\n", "").split(" ")) for x in file.readlines())

def printPartitionList():
    print("{:>5} {:>8} {:>8} {:>8} {:>15} {:>25}".format('No', 'Size', 'Job', 'Busy', 'Time Remaining', 'Internal Fragmentation'))

    for partition in partition_list:
        print("{:>5} {:>8} {:>8} {:>8} {:>15} {:>25}".format(partition.id, 
        partition.size, 
        'NULL' if partition.job is None else partition.job.id, 
        'True' if partition.busy else 'False', 
        partition.time,
        str(int(partition.size) - int(partition.job.size)) if partition.busy else '0'))

    print("Jobs: " + (", ").join(list(job.id for job in job_list)))
    print("Logs:\n" + ("\n").join(logs))

def assignJobFirstFit():
    for job in job_list:
        for x in partition_list:
            if job.size <= x.size and not x.busy:
                tempJob = job
                try:
                    job_list.remove(job)
                except ValueError:
                    break
                x.busy = True
                x.job = tempJob
                x.time = tempJob.time
                logs.append(f"Assigned job {tempJob.id} ({tempJob.size}) to partition {x.id} ({x.size}).")
                x.startWork()
                break
            else:
                continue

def assignJobBestFit():
    for job in job_list:
        best = None

        for part in partition_list:
            if job.size <= part.size and not part.busy:
                if best is None:
                    best = part
                elif best.size > part.size:
                    best = part
                else:
                    continue
            else:
                continue

        if best is not None:
            tempJob = job
            try:
                job_list.remove(job)
            except ValueError:
                break
            best.busy = True
            best.job = tempJob
            best.time = tempJob.time
            logs.append(f"Assigned job {tempJob.id} ({tempJob.size}) to partition {best.id} ({best.size}).")
            best.startWork()
        else:
            continue

#cant get it to work
def checkInsufficient():
    for job in job_list:
        enuf = False
        for part in partition_list:
            if job.size <= part.size:
                enuf = True
                break
            else:
                continue
        
        if enuf:
            continue

        logs.append(f"Moving job {job.id} to error, due to lack of memory.")
        error.append(job)
        job_list.remove(job)

def main():
    start = timer()
    checkInsufficient()

    if not jobType:
        assignJobFirstFit()
    else:
        assignJobBestFit()

    printPartitionList()

    while(not all(list(not part.busy for part in partition_list))):
        cls()
        printPartitionList()
        sleep(.5)

    printPartitionList()
    end = timer()
    print("Time Taken = " + str(end-start))

if __name__ == "__main__":
    for x in readjobs("job_list.txt"):
        job_list.append(Job(x[0], x[2], x[1]))

    for x in readpartitions("partition_list.txt"):
        partition_list.append(Partition(x[0], x[1]))


    jobType = True

    x = threading.Thread(target=main)
    x.start()


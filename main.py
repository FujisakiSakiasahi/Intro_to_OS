import threading
from time import sleep

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
    print("{:>5} {:>8} {:>8} {:>8} {:>15}".format('No', 'Size', 'Job', 'Busy', 'Time Remaining'))

    for partition in partition_list:
        print("{:>5} {:>8} {:>8} {:>8} {:>15}".format(partition.id, 
        partition.size, 
        'NULL' if partition.job is None else partition.job.id, 
        'True' if partition.busy else 'False', 
        partition.time))

if __name__ == "__main__":
    job_list = []
    partition_list = []
    job_waiting_list = []

    for x in readjobs("job_list.txt"):
        job_list.append(Job(x[0], x[2], x[1]))

    for x in readpartitions("partition_list.txt"):
        partition_list.append(Partition(x[0], x[1]))

    printPartitionList()

    for job in job_list:
        for x in partition_list:
            if job.size <= x.size and not x.busy:
                x.job = job
                x.busy = True
                x.time = job.time
                print(f"Assigned job {job.id} to partition {x.id}.")
                x.startWork()
                break
            else:
                continue
        job_waiting_list.append(job)
        print(f"Added job {job.id} to waiting list.")

    print()
    print()

    while(True):
        cls()
        printPartitionList()
        sleep(.5)



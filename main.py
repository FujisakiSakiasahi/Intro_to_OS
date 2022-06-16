import os
import threading
from time import sleep
from timeit import default_timer as timer

job_list = []
waiting_list = []
partition_list = []
logs = []
error = []
avgWait = [int(0), int(0)]
jobType = False #false = first fit / true = best fit

def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

class Partition:
    def __init__(self, id, size:int):
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
    def __init__(self, id, size:int, time):
        self.id = id
        self.size = size
        self.time = int(time)
        self.waitingTime = int(0)

    @threaded
    def waiting(self):
        while( self in waiting_list ):
            self.waitingTime += 1
            sleep(1)


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
    print("{:>6} {:>8} {:>8} {:>8} {:>15} {:>25} {:>12}".format('No', 'Size', 'Job', 'Busy', 'Time Remaining', 'Internal Fragmentation', '% Used'))

    for partition in partition_list:
        print("{:>6} {:>8} {:>8} {:>8} {:>15} {:>25} {:>12}".format(partition.id, 
        partition.size, 
        'NULL' if partition.job is None else partition.job.id, 
        'True' if partition.busy else 'False', 
        partition.time,
        str(partition.size - partition.job.size) if partition.busy else '0',
        "{:.2f}".format((partition.job.size / partition.size) * 100) if partition.busy else '0.00'))

    print("{:>6} {:>8} {:>8} {:>8} {:>15} {:>25} {:>5}{:>7}".format('Total', sum(part.size for part in partition_list), 'Used:', 
    f"{sum(part.busy for part in partition_list)}/{len(partition_list)}", 
    'Total Frag', sum((part.size-part.job.size) if part.busy else 0 for part in partition_list), 
    "Avg:",
    str("{:.2f}".format((sum((part.job.size) if part.busy else 0 for part in partition_list) / sum(part.size for part in partition_list) * 100)))))

    print("\nJob List: " + (", ").join(list(job.id for job in job_list)))
    print("Waiting List: " + (", ").join(list(f"{job.id}({job.waitingTime})" for job in waiting_list)))
    print("\nLogs:\n" + ("\n").join(logs))

def assignJobFirstFit():
    for job in waiting_list:
        for x in partition_list:
            if job.size <= x.size and not x.busy:
                tempJob = job
                try:
                    waiting_list.remove(job)
                except ValueError:
                    break
                x.busy = True
                x.job = tempJob
                x.time = tempJob.time
                used = "{:.2f}% used".format((job.size / x.size) * 100)
                logs.append(f"Assigned job {tempJob.id} ({tempJob.size})({tempJob.waitingTime}) to partition {x.id} ({x.size}) ({used}).")
                x.startWork()
                avgWait[0] += tempJob.waitingTime
                avgWait[1] += 1
                break
            else:
                continue
    
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
                used = "{:.2f}% used".format((job.size / x.size) * 100)
                logs.append(f"Assigned job {tempJob.id} ({tempJob.size})(0) to partition {x.id} ({x.size}) ({used}).")
                x.startWork()
                break
            else:
                continue

        if job in job_list:
            tempJob = job
            try:
                job_list.remove(job)
            except ValueError:
                break
            waiting_list.append(tempJob)
            tempJob.waiting()


def assignJobBestFit():
    for job in waiting_list:
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
                waiting_list.remove(job)
            except ValueError:
                break
            best.busy = True
            best.job = tempJob
            best.time = tempJob.time
            used = "{:.2f}% used".format((job.size / best.size) * 100)
            logs.append(f"Assigned job {tempJob.id} ({tempJob.size})({tempJob.waitingTime}) to partition {best.id} ({best.size}) ({used}).")
            best.startWork()
            avgWait[0] += tempJob.waitingTime
            avgWait[1] += 1
        else:
            continue

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
            used = "{:.2f}% used".format((job.size / best.size) * 100)
            logs.append(f"Assigned job {tempJob.id} ({tempJob.size})(0) to partition {best.id} ({best.size}) ({used}).")
            best.startWork()
        else:
            if job in job_list:
                tempJob = job
                try:
                        job_list.remove(job)
                except ValueError:
                    break
                waiting_list.append(tempJob)
                tempJob.waiting()

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

    cls()
    printPartitionList()
    print()
    end = timer()
    print("Job type: " + str("Best Fit" if jobType else "First Fit"))
    print("Time Taken = " + "{:.4f}s".format(end-start))
    print("Average Time taken per job: " + str((end-start) / 25)) #avg jobs processed per time unit
    print("Items added to waiting list: " + str(avgWait[1])) #waiting queue length
    print("Average Time in Waiting List: " + "{:.2f}".format(avgWait[0] / avgWait[1])) #average time in waiting queue
    # print("Weiharng eh idea: " + "{:.2f}".format(avgWait[0] / 25))
    

if __name__ == "__main__":
    for x in readjobs("job_list.txt"):
        job_list.append(Job(x[0], int(x[2]), x[1]))

    for x in readpartitions("partition_list.txt"):
        partition_list.append(Partition(x[0], int(x[1])))
    
    cls()

    choice = 0

    while(True):
        choice = int(input ("What type do you want to run the job with? (1=First Fit/2=Best Fit): "))
        if choice == 1 or choice == 2:
            break

    jobType = False if choice == 1 else True

    x = threading.Thread(target=main)
    x.start()


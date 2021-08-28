#!/usr/bin/env python3

import os
from sys import executable
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# EXECUTE THIS SCRIPT IN BASE DIRECTORY!!!

NUM_EXPERIMENTS_PER_SETUP = 3
THREADS = [1, 2, 8, 16]

def gen_setups():
    threads = THREADS
    counts_per_thread = [10000, 100000, 1000000, 2000000, 4000000, 6000000, 8000000, 10000000]
    return [[thread, count] for thread in threads for count in counts_per_thread]

def build():
    os.system("g++ main.cpp mcs_lock.cpp -lpthread -Ofast -o main")

def run_all():
    if not os.path.exists("./res"): os.mkdir("./res") # create result directory inside bin    
    for setup in gen_setups():
        thread = setup[0]
        count = setup[1]
        args = " " +  str(thread) + " " + str(count)
        print("T:" + str(thread) + " C:" + str(count))
        for i in range(NUM_EXPERIMENTS_PER_SETUP):
            result_file = "T" + str(thread) + "C" + str(count)  + ".log" + str(i)
            print(" Trial:" + str(i))
            ret = os.system("./main"  + args + " > ./res/" + result_file +" 2>&1")
            if ret != 0:
                print("Error. Stopping")
                exit(0)

def plot_all():
    # plot time
    os.chdir("./res") # move to result file
    if not os.path.exists("./plots"): os.mkdir("./plots") # create plot directory inside res
    time_taken_mutex = {}
    time_taken_mcs = {}
    for setup in gen_setups():
        thread = setup[0]
        if thread not in time_taken_mutex:
            time_taken_mutex[thread] = []
        if thread not in time_taken_mcs:
            time_taken_mcs[thread] = []
        count = setup[1]
        average_time_mutex = 0
        average_time_mcs = 0
        for i in range(NUM_EXPERIMENTS_PER_SETUP):
            result_file = "T" + str(thread) + "C" + str(count)  + ".log" + str(i)
            result_file = open(result_file)
            for line in result_file:
                line = line.strip().split()
                if not line: continue
                if line[0] == "std::mutex":
                    time_mutex = float(line[2])
                if line[0] == "MCSLock":
                    time_mcs = float(line[2])
            result_file.close()
            average_time_mutex += time_mutex
            average_time_mcs += time_mcs
        average_time_mutex /= NUM_EXPERIMENTS_PER_SETUP
        average_time_mcs /= NUM_EXPERIMENTS_PER_SETUP
        time_taken_mutex[thread].append([count, average_time_mutex])
        time_taken_mcs[thread].append([count, average_time_mcs])


    markers = ['o', 'v', 's', 'p', 'P', '*', 'X', 'D', 'd', '|', '_']

    plt.style.use('seaborn-dark')

    for i, thread in enumerate(THREADS):
        fig, ax = plt.subplots(1, 1, figsize=(7,4))
        res_mcs = np.array(time_taken_mcs[thread]).T
        res_mutex = np.array(time_taken_mutex[thread]).T
        ax.plot(res_mutex[0], res_mutex[1], markers[0]+'-', label = "std::mutex")
        ax.plot(res_mcs[0], res_mcs[1], markers[1]+'-', label = "MCSLock")

        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        ax.set_xlabel("Counts per thread")
        ax.set_ylabel("Time (millisec)")
        ax.set_title("Comparison of lock implementations using " + str(thread) + " thread(s)")
        ax.grid()
    
        ax.legend(loc="best")
        fig.savefig("./plots/lockwithT{}.png".format(thread))
        print("output is saved in ./res/plots/")
    os.chdir("../") # go back to base directory

if __name__ == "__main__":
    # build()
    # run_all()
    plot_all()
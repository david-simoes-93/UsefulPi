import os
import matplotlib.pyplot as mpl
from datetime import datetime
import numpy as np

# This function reads all .log files in the same folder and saves speedtest.pdf and speedtest_per_hour.pdf
def make_plots():
    # there are dl vars for Download results, and ul vars for Upload results
    dl_list = []
    ul_list = []
    # we can also map it by hour
    dl_by_hour = [[] for x in range(24)]
    ul_by_hour = [[] for x in range(24)]

    # iterate over all .log files
    print("Reading logs...")
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    files.sort()
    for f in files:
        if ".log" not in f:
            continue
        #print(f)
        my_file = open(f, 'r')
        lines = my_file.readlines()
        # iterate over lines in each file
        for line in lines:
            # clean line
            while "  " in line:
                line = line.replace("  ", " ")
            line = line.strip()
            # extract hour from filename
            hour = int(datetime.utcfromtimestamp(int(f.split(".")[0])).strftime('%H'))
            # extract DL or UL value from line
            if "Download" in line:
                val = float(line.split(" ")[1]) if "FAILED" not in line else 0
                dl_list.append(val)
                dl_by_hour[hour].append(val)
            if "Upload" in line:
                val = float(line.split(" ")[1]) if "FAILED" not in line else 0
                ul_list.append(val)
                ul_by_hour[hour].append(val)

    # plot ALL read values
    print("Saving speedtest.pdf")
    mpl.plot(dl_list)
    mpl.plot(ul_list)
    mpl.savefig("speedtest.pdf")
    mpl.clf()

    # plot average hourly values
    print("Saving speedtest_per_hour.pdf")
    mpl.xlim([0, 23])
    mpl.ylim([0, 120])
    mpl.xlabel("Hours")
    mpl.ylabel("Average MB/s")
    mpl.xticks(range(24))
    dl_day = []
    ul_day = []
    for hour in dl_by_hour:
        dl_day.append(np.average(hour))
    mpl.plot(dl_day, label="Download")
    for hour in ul_by_hour:
        ul_day.append(np.average(hour))
    mpl.plot(ul_day, label="Upload")
    mpl.legend()
    mpl.savefig("speedtest_per_hour.pdf")

if __name__ == "__main__":
    make_plots()

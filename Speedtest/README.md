# Speedtest

Add a cronjob that runs every hour to run a speedtest and add it to a home directory.

    sudo apt install speedtest-cli
    mkdir /home/pi/speedtests
    crontab -e
        0 * * * * speedtest > "/home/pi/speedtests/$(date +\%s).log"

To visualize the data, prepare an environment and run the `plot_speedtests.py` script

    sudo apt install libatlas-base-dev
    python3 -m venv venv
    source venv/bin/activate
    pip install matplotlib numpy
    python plot_speedtests.py

Then, copy these from your RPi onto your machine with `scp`

    scp my_pi:~/speedtests/*.pdf .

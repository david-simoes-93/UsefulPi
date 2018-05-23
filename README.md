# UsefulPi

For starters, get [Raspbian Lite](https://www.raspberrypi.org/downloads/raspbian/). [Flash](https://www.raspberrypi.org/documentation/installation/installing-images/) it onto an SD card with `dd` (for purists) or [Etcher](https://etcher.io/) (for new users), [enable ssh](https://www.raspberrypi.org/documentation/remote-access/ssh/README.md) (easiest way is to create a file called `ssh` in the boot partition of the SD card), and connect the RPi directly to your laptop with an Ethernet cable (configuring the connection [properly](https://stackoverflow.com/questions/16040128/hook-up-raspberry-pi-via-ethernet-to-laptop-without-router)). Connect to the RPi and have fun!

    ssh pi@192.168.1.100
        raspberry

I suggest starting with an update, setting environment variables, and readying a session manager like Tmux. 

    sudo apt update
    sudo apt upgrade
    nano .bashrc
        export LANG=en_GB.UTF-8
        export LC_ALL=en_GB.UTF-8
        export LC_CTYPE=en_GB.UTF-8
    sudo apt install tmux

All schematics used were for Raspberry Pi 2B (my model), datasheet below.

![raspib-gpio_reference](https://user-images.githubusercontent.com/9117323/37006687-656076ba-20d1-11e8-96f2-0f03cf983224.png)

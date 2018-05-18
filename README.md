# UsefulPi

For starters, get Raspbian Lite. Flash it onto an SD card with dd, create an ssh file in boot folder, and connect the pi directly to your laptop. ssh into it.

Update, set environment variables, ready a session manager like Tmux 

    sudo apt update
    sudo apt upgrade
    nano .bashrc
        export LANG=en_GB.UTF-8
        export LC_ALL=en_GB.UTF-8
        export LC_CTYPE=en_GB.UTF-8
    sudo apt install tmux

All schematics used were for Raspberry Pi 2B (my model), datasheet below

![raspib-gpio_reference](https://user-images.githubusercontent.com/9117323/37006687-656076ba-20d1-11e8-96f2-0f03cf983224.png)

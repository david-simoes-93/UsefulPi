# FTP Server

Similar to a NAS, you can host files in your RPi using FTP, as seen [here](https://howtoraspberrypi.com/setup-ftp-server-raspberry-pi/).

    sudo apt install proftpd
        inetd
    sudo nano /etc/proftpd/proftpd.conf
        TimeoutIdle          600
        DefaultRoot ~
    sudo service proftpd reload

Just connect with your RPi account on the proper IP, like this

    ftp://192.168.1.100

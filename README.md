# UsefulPi

Update, set environment variables, ready a session manager like Tmux 

    sudo apt update
    sudo apt upgrade
    nano .bashrc
        export LANG=en_GB.UTF-8
        export LC_ALL=en_GB.UTF-8
        export LC_CTYPE=en_GB.UTF-8
    sudo apt install tmux

Make a [NAS](https://www.howtogeek.com/139433/how-to-turn-a-raspberry-pi-into-a-low-power-network-storage-device/) with 2 HDDs, using Samba. One of the HDDs gets backed-up into the other every night

    sudo mkdir /media/USBHDD1
    sudo mkdir /media/USBHDD2
    sudo mount -t auto /dev/sda1 /media/USBHDD1
    sudo mount -t auto /dev/sdb1 /media/USBHDD2
    sudo mkdir /media/USBHDD1/shares
    sudo mkdir /media/USBHDD2/shares
    sudo chmod a+rwx /media/USBHDD1
    sudo chmod a+rwx /media/USBHDD2
    sudo apt install samba samba-common-bin exfat-utils
    sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.old
    sudo nano /etc/samba/smb.conf
        [Backup]
        comment = Backup Folder
        path = /media/USBHDD1/shares
        valid users = @users
        force group = users
        create mask = 0660
        directory mask = 0771
        read only = no
    sudo /etc/init.d/samba restart
    sudo useradd bluemoon93 -m -G users
    sudo passwd bluemoon93
    sudo smbpasswd -a bluemoon93
    
    sudo apt install rsync
    crontab -e
        0 5 * * * rsync -av --delete /media/USBHDD1/shares /media/USBHDD2/shares/
        
To unmount

    sync
    sudo umount /dev/sda1
    sudo umount /dev/sdb1
    
Make a [VPN](https://www.howtogeek.com/51237/setting-up-a-vpn-pptp-server-on-debian/) using PPTP

    sudo apt install pptpd
    sudo nano /etc/pptpd.conf
        localip 192.168.1.64
        remoteip 192.168.1.100-200
    sudo nano /etc/ppp/pptpd-options
        ms-dns 8.8.8.8
        ms-dns 8.8.4.4
    sudo nano /etc/ppp/chap-secrets
        bluemoon93<TAB>*<TAB>mypassword<TAB>*
    sudo nano /etc/rc.local
        sudo service pptpd restart
   

Control a Fan based on temperature

    pip3 install psutil raspi
    sudo nano /etc/rc.local
        sudo -u pi -H sh -c "cd /home/pi/UsefulPi; python3 fan.py &"
        
I used the circuit below, with a [2N2222A Transistor](http://web.mit.edu/6.101/www/reference/2N2222A.pdf), but I've been told it should have been a VN2222. For 2N2222A, the resistance should be serial, about 2.2k.

![fan](https://user-images.githubusercontent.com/9117323/36357487-8f6cb4d2-14f6-11e8-8f86-0c9446cbec01.png)

All schematics used were for Raspberry Pi 2B (my model), datasheet below

![raspib-gpio_reference](https://user-images.githubusercontent.com/9117323/37006687-656076ba-20d1-11e8-96f2-0f03cf983224.png)

# UsefulPi

Update and set env variables

    sudo apt update
    sudo apt upgrade
    nano .bashrc
        export LANG=en_GB.UTF-8
        export LC_ALL=en_GB.UTF-8
        export LC_CTYPE=en_GB.UTF-8
    sudo apt install tmux

Make a [NAS](https://www.howtogeek.com/139433/how-to-turn-a-raspberry-pi-into-a-low-power-network-storage-device/)!

    sudo mkdir /media/USBHDD1
    sudo mkdir /media/USBHDD2
    sudo mount -t auto /dev/sda1 /media/USBHDD1
    sudo mount -t auto /dev/sdb1 /media/USBHDD2
    sudo mkdir /media/USBHDD1/shares
    sudo mkdir /media/USBHDD2/shares
    sudo chmod a+rwx /media/USBHDD1
    sudo chmod a+rwx /media/USBHDD2
    sudo apt-get install samba samba-common-bin
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
    
    sudo apt-get install rsync
    crontab -e
        0 5 * * * rsync -av --delete /media/USBHDD1/shares /media/USBHDD2/shares/
    
Make a [VPN](https://www.howtogeek.com/51237/setting-up-a-vpn-pptp-server-on-debian/)

    sudo apt install pptpd
    sudo nano /etc/pptpd.conf
        localip 192.168.1.64
        remoteip 192.168.1.100-200
    sudo nano /etc/ppp/pptpd-options
        ms-dns 8.8.8.8
        ms-dns 8.8.4.4
    sudo nano /etc/ppp/chap-secrets
        bluemoon93<TAB>*<TAB>mypassword<TAB>*
    sudo service pptpd restart


# UsefulPi

Update, set environment variables, ready a session manager like Tmux 

    sudo apt update
    sudo apt upgrade
    nano .bashrc
        export LANG=en_GB.UTF-8
        export LC_ALL=en_GB.UTF-8
        export LC_CTYPE=en_GB.UTF-8
    sudo apt install tmux

Make a [NAS](https://www.howtogeek.com/139433/how-to-turn-a-raspberry-pi-into-a-low-power-network-storage-device/) with 2 HDDs, one of which gets backed-up into the other every night

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
    sudo service pptpd restart

Control USB ports and connected disks by [safely removing them](https://askubuntu.com/questions/532586/what-is-the-command-line-equivalent-of-safely-remove-drive), [turning off the power](https://stackoverflow.com/questions/4702216/controlling-a-usb-power-supply-on-off-with-linux) , [ejecting it](https://unix.stackexchange.com/questions/35508/eject-usb-drives-eject-command), or just [mounting/unmounting](https://askubuntu.com/questions/37767/how-to-access-a-usb-flash-drive-from-the-terminal)


    # Turning off
    udisksctl unmount -b /dev/sdb1
    udisksctl power-off -b /dev/sdb
    sudo nano /sys/bus/usb/devices/usb1/power/autosuspend_delay_ms
        0
    sudo nano /sys/bus/usb/devices/usb1/power/control
        auto
    sudo eject /dev/sda
    sudo umount /media/usb
    # Turning on
    sudo nano /sys/bus/usb/devices/usb1/power/autosuspend_delay_ms
        2000
    sudo nano /sys/bus/usb/devices/usb1/power/control
        on
    sudo mount -t auto /dev/sda1 /media/USBHDD1


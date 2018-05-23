# Turning RPi into a NAS

Make a [NAS](https://www.howtogeek.com/139433/how-to-turn-a-raspberry-pi-into-a-low-power-network-storage-device/) with 2 HDDs, using Samba.

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

To save energy, make sure the HDDs [spin-down](https://askubuntu.com/questions/39760/how-can-i-control-hdd-spin-down-time) when not being used

    sudo nano /sys/bus/usb/devices/usb1/power/autosuspend_delay_ms
        0
    sudo nano /sys/bus/usb/devices/usb1/power/control
        auto
    sudo nano /sys/bus/usb/devices/usb2/power/autosuspend_delay_ms
        0
    sudo nano /sys/bus/usb/devices/usb2/power/control
        auto

If you want back-ups, have one of the HDDs being copied into the other one every night

    sudo apt install rsync
    crontab -e
        0 5 * * * rsync -av --delete /media/USBHDD1/shares /media/USBHDD2/shares/
        

To unmount the HDDs, if you want to turn them off

    sync
    sudo umount /dev/sda1
    sudo umount /dev/sdb1
    
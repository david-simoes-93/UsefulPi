
[WIP] Control USB ports and connected disks by [safely removing them](https://askubuntu.com/questions/532586/what-is-the-command-line-equivalent-of-safely-remove-drive), [turning off the power](https://stackoverflow.com/questions/4702216/controlling-a-usb-power-supply-on-off-with-linux) , [ejecting it](https://unix.stackexchange.com/questions/35508/eject-usb-drives-eject-command), [turning down the spin-down time](https://askubuntu.com/questions/39760/how-can-i-control-hdd-spin-down-time), or just [mounting/unmounting](https://askubuntu.com/questions/37767/how-to-access-a-usb-flash-drive-from-the-terminal). More [info](http://www.spencerstirling.com/computergeek/powersaving.html)


    # Turning off
    sync
    udisksctl unmount -b /dev/sda1
    udisksctl power-off -b /dev/sda1
    
    sudo nano /sys/bus/usb/devices/usb1/power/autosuspend_delay_ms
        0
    sudo nano /sys/bus/usb/devices/usb1/power/control
        auto
    sudo eject /dev/sda1
    sudo umount /dev/sda1
    sudo hdparm -S 25 /dev/sda1
    # Turning on
    sudo nano /sys/bus/usb/devices/usb1/power/autosuspend_delay_ms
        2000
    sudo nano /sys/bus/usb/devices/usb1/power/control
        on
    sudo mount -t auto /dev/sda1 /media/USBHDD1
    udisksctl mount -b /dev/sdf

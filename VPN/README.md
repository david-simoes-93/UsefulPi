#Turn the RPi into a VPN

Make a [VPN](https://www.howtogeek.com/51237/setting-up-a-vpn-pptp-server-on-debian/) using PPTP

    sudo apt install pptpd
    sudo nano /etc/pptpd.conf
        localip 192.168.1.64
        remoteip 192.168.1.100-200
    sudo nano /etc/ppp/pptpd-options
        ms-dns 1.1.1.1
        ms-dns 1.0.0.1
    sudo nano /etc/ppp/chap-secrets
        bluemoon93<TAB>*<TAB>mypassword<TAB>*
    sudo nano /etc/rc.local
        sudo service pptpd restart
   
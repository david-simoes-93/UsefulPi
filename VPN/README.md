# Turn the RPi into a VPN

Make a [VPN](https://www.howtogeek.com/51237/setting-up-a-vpn-pptp-server-on-debian/) using PPTP.

    sudo apt install pptpd
    sudo nano /etc/pptpd.conf
        localip 192.168.1.64        # This is the RPi IP
        remoteip 192.168.1.100-200  # The range of IPs for clients connecting
    sudo nano /etc/ppp/pptpd-options
        ms-dns 1.1.1.1
        ms-dns 1.0.0.1
    sudo nano /etc/ppp/chap-secrets
        bluemoon93<TAB>*<TAB>mypassword<TAB>*   # Accounts and passwords
    sudo nano /etc/rc.local
        sudo service pptpd restart  # Before the exit line
   
Then forward port 1723 in your Router

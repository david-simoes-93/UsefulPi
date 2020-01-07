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
        bluemoon93<TAB>pptpd<TAB>mypassword<TAB>*   # Accounts and passwords
    sudo nano /etc/sysctl.conf
        net.ipv4.ip_forward=1
    sudo nano sysctl -p
    sudo nano /etc/rc.local
        iptables -I INPUT -p tcp --dport 1723 -m state --state NEW -j ACCEPT
        iptables -I INPUT -p gre -j ACCEPT
        iptables -t nat -I POSTROUTING -o eth0 -j MASQUERADE        # Replace eth0 for whatever interface your Pi uses to connect to the Internet (use 'ip addr' to find it)
        iptables -I FORWARD -p tcp --tcp-flags SYN,RST SYN -s 192.168.1.0/24 -j TCPMSS  --clamp-mss-to-pmtu
    sudo nano /etc/rc.local
        sudo service pptpd restart  # Before the exit line
   
Then forward port 1723 in your Router

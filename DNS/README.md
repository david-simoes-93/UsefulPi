# DNS Server

Speed up your Internet surfing by using the RPi as a DNS server! Different guides [here](https://www.pcworld.com/article/3200117/linux/how-to-use-raspberry-pi-as-dns-server-with-dnsmasq.html), [here](https://www.1and1.com/digitalguide/server/configuration/how-to-make-your-raspberry-pi-into-a-dns-server/), or [here](https://www.raspberrypi.org/forums/viewtopic.php?t=46154). I like the last one, all you have to do to install is

    curl "https://raw.github.com/stephen-mw/raspberrypi/master/roles/dnsmasq_server" | sudo sh
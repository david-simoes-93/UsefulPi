#Control your GPIO

For example, control a fan based on temperature

![fancase](https://cdn.itead.cc/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/t/r/transparent_acrylic_case_cooling_fan_for_raspberry_pi_3_2_b-1.jpg)

    pip3 install psutil raspi
    sudo nano /etc/rc.local
        sudo -u pi -H sh -c "cd /home/pi/UsefulPi/GPIO; python3 fan.py &"
        

You can use one of the circuits below, with a [2N2222A Transistor](http://web.mit.edu/6.101/www/reference/2N2222A.pdf), or a [VN2222 Transistor](https://www.mouser.com/ds/2/268/VN2222-1181471.pdf). For the diode, any fast-recovery diode should work, although I used the first I found lying around, [1N4001](https://www.diodes.com/assets/Datasheets/ds28002.pdf).

![fan](https://user-images.githubusercontent.com/9117323/36357487-8f6cb4d2-14f6-11e8-8f86-0c9446cbec01.png)

#!/bin/sh
#sleep 30
seconds=5
sudo systemctl stop hostapd.service
sudo systemctl stop dnsmasq.service
sudo systemctl stop dhcpcd.service

#when wlan9 exist it must be deleted first
if [ -e /sys/class/net/wlan9 ]
then
    sudo iw dev wlan9 del
fi

#before adding an access point to the same device it must be turned off
sudo ifconfig wlan0 down
#adding wlan9 as access point to wlan0"
sudo iw dev wlan0 interface add wlan9 type __ap
#enable turned off wlan9
sudo ifconfig wlan9 up

#start services, mitigating race conditions
#start access point
sudo systemctl start hostapd.service
sleep "${seconds}"
#restart dhcpcd
sudo systemctl restart dhcpcd.service
sleep "${seconds}"
#start dhcp server
sudo systemctl start dnsmasq.service

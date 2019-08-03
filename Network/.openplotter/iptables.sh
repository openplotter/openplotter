#!/bin/sh
internet=$1
router=$2

base=auto

if [ $internet == $base ];
then
	internet=$(ip -4 route list 0/0 | head -n 1 | cut -d " " -f5)
fi

#when the interface doesn't exists
#result=$(ls /sys/class/net | grep "$internet")
#if [ -z $result ]
#then
#	internet=$(ip -4 route list 0/0 | head -n 1 | cut -d " " -f5)
#fi

#echo "$internet"

sudo iptables -F
sudo iptables -t nat -A POSTROUTING -o "${internet}" -j MASQUERADE
sudo iptables -A FORWARD -i "${internet}" -o "${router}" -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i "${router}" -o "${internet}" -j ACCEPT

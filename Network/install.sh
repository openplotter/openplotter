#!/bin/sh
function disable_dhcp_server_and_ap {
	erg=$(systemctl status dnsmasq | grep 'enabled;')
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		sudo systemctl disable dnsmasq
	fi
	
	erg=$(systemctl status hostapd | grep 'enabled;')
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		sudo systemctl disable hostapd
	fi	
}

function enable_dhcp_server_and_ap {
	erg=$(systemctl status dnsmasq | grep disabled)
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		sudo systemctl enable dnsmasq
	fi

	erg=$(systemctl status hostapd | grep disabled)
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		sudo systemctl enable hostapd
	fi	
}

function disable_bridge {
	erg=$(systemctl status systemd-networkd | grep 'enabled;')
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		sudo systemctl disable systemd-networkd
	fi
}

function enable_bridge {
	erg=$(systemctl status systemd-networkd | grep 'disabled;')
	chrlen=${#erg}
	if [ $chrlen -gt 0 ]
	then
		sudo systemctl enable systemd-networkd
	fi
}

function delete_file {
	if [ -e $1 ]
	then
		sudo rm $1
	fi
}

function copy_file {
	if [ -e $1 ]
	then
		sudo cp $1 $2
	fi
}

#main
response=$1

#set back to default debian
if [[ "$response" = "uninstall" ]]; then
	#no AP (set back to original setting)
	disable_dhcp_server_and_ap

	sudo cp dhcpcd.conf /etc
	sudo echo '#!/bin/sh' > ~/.openplotter/start-ap-managed-wifi.sh
	#sudo cp network/interfaces /etc/network

	delete_file /etc/network/interfaces.d/ap
	delete_file /etc/udev/rules.d/72-wireless.rules
	delete_file /etc/udev/rules.d/11-openplotter-usb0.rules
	
	if [ -e /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant_wlan9 ]
	then
		sudo rm /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant_wlan9
		sudo cp ~/.config/openplotter/Network/dhcpcd-hooks/10-wpa_supplicant /lib/dhcpcd/dhcpcd-hooks
	fi

	#uninstall bridge
	disable_bridge
	delete_file /etc/systemd/network/bridge-br0.network
	delete_file /etc/systemd/network/bridge-br0-slave.network
	delete_file /etc/systemd/network/bridge-br0.netdev
	
#set to access point
else
	sudo cp dhcpcd.conf /etc
	sudo cp dnsmasq.conf /etc
	sudo cp .openplotter/start-ap-managed-wifi.sh ~/.openplotter
	sudo cp .openplotter/iptables.sh ~/.openplotter
	sudo cp .openplotter/start1.sh ~/.openplotter

	sudo cp hostapd/hostapd.conf /etc/hostapd
#	sudo cp network/interfaces /etc/network
#	sudo cp network/interfaces.d/ap /etc/network/interfaces.d

	if [ -e /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant ]
	then
		sudo rm /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant
		sudo cp ~/.config/openplotter/Network/dhcpcd-hooks/10-wpa_supplicant_wlan9 /lib/dhcpcd/dhcpcd-hooks
	fi

	copy_file udev/rules.d/11-openplotter-usb0.rules /etc/udev/rules.d

	enable_dhcp_server_and_ap
	
	#bridge yes/no
	if [ -e systemd/network/bridge-br0.network ]
	then
		#enable bridge
		copy_file systemd/network/bridge-br0.network /etc/systemd/network
		copy_file systemd/network/bridge-br0-slave.network /etc/systemd/network
		copy_file systemd/network/bridge-br0.netdev /etc/systemd/network
		enable_bridge
	else
		disable_bridge
		delete_file /etc/systemd/network/bridge-br0.network
		delete_file /etc/systemd/network/bridge-br0-slave.network
		delete_file /etc/systemd/network/bridge-br0.netdev
	fi
	
	#station and ap yes/no
	if [ -e ~/.openplotter/Network/.openplotter/start1.sh ]
	then
		result=$(cat ~/.openplotter/Network/.openplotter/start1.sh | grep __ap)
		#result2=$(expr length $result)
		#echo $result2
		if [ -z "$result" ]
		then
			sudo cp udev/rules.d/72-wireless.rules /etc/udev/rules.d
		else
			delete_file /etc/udev/rules.d/72-wireless.rules
		fi
	fi

fi


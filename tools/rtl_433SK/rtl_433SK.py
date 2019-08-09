#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2019 by sailoog <https://github.com/sailoog/openplotter>
#                     e-sailing <https://github.com/e-sailing/openplotter>
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

# This tool should receive data from wireless temperature, humidity sensors based 
# on 433 MHz or 868 Mhz convert the data and send it to the signal k server

import signal, sys, os, time, socket, subprocess, ujson
import shlex

op_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')
sys.path.append(op_folder+'/classes')

#for sensor type see: rtl_433 -h

#frequenz ="-f 865985K -s 1024k "	#for 868Mhz
#frequenz ="-f 868M -s 1024k "	#for 868Mhz
frequenz =""					#for 433.2Mhz

# In the config_j you can choose the signal K path for your values.
# To get the right setting start "rtl_433 -f json" and identify the characteristics of your sensors
# The identification of each sensor depends on the id (and on the channel if exist).
# The "freq" is only added for information
# This has been done with rtl_433 version 18.12-253


config_j = '''{
	"sensor": [
		{
			"id": 11361,
			"unit": 22,
			"learn": 0,
			"code": "environment.lastmovement",
			"freq": 434040
		},
		{
			"id": 5,
			"rid": 68,
			"channel": 1,
			"temperature_C": "environment.inside.pearl.temperature",
			"humidity": "environment.inside.pearl.humidity",
			"freq": 433977
		},
		{
			"id": 86,
			"channel": 3,
			"temperature_C": "environment.inside.refrigerator.temperature",
			"humidity": "environment.inside.refrigerator.humidity",
			"freq": 433977
		},
		{
			"msg_type": 0,
			"id": 151,
			"temperature_C": "environment.outside.temperature",
			"humidity": "environment.outside.humidity",
			"direction_deg": "environment.wind.angleTrueGround",
			"speed": "environment.wind.speedOverGround",
			"gust": "environment.gust",
			"rain": "environment.rain",
			"freq": 865985
		}
	]
}'''


# Control-C signal handler to suppress exceptions if user presses Control C
# This is totally optional.
def signal_handler(sig, frame):
	print('You pressed Ctrl+C!!!!')
	process.kill()
	sys.exit(0)
		

if len(sys.argv)>1:
	if sys.argv[1]=='settings':
		print('No config file or gui! Changes must be made in the python file')
	exit
else:

	signal.signal(signal.SIGINT, signal_handler)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	config = ujson.loads(config_j)
	process = subprocess.Popen(('rtl_433 '+ frequenz +'-F json').split(' '),stdout=subprocess.PIPE)
	while True:
		output = process.stdout.readline()
		if process.poll() is not None and output == '':	    break
		if output:
			data = ujson.loads(output)
			if "id" in data:
				print(1, data["id"]) 
				for configSensor in config["sensor"]:

					if configSensor["id"] == data["id"]:
						type_rtl = str(data["id"])
						found = True
						if "channel" in configSensor:
							if data["channel"] == configSensor["channel"]:
								type_rtl = type_rtl + '.' + str(data["channel"])
							else:
								found = False
						
						if found:
							Erg=''
							if "temperature_C" in data:
								Erg += '{"path": "'+configSensor["temperature_C"]+'","value":'+str(float(data["temperature_C"])+273.15)+'},'
							if "humidity" in data:
								Erg += '{"path": "'+configSensor["humidity"]+'","value":'+str(data["humidity"])+'},'
							if "direction_deg" in data:
								Erg += '{"path": "'+configSensor["direction_deg"]+'","value":'+str(float(data["direction_deg"])*0.017453292)+'},'
							if "speed" in data:
								Erg += '{"path": "'+configSensor["speed"]+'","value":'+str(float(data["speed"]))+'},'
							if "gust" in data:
								Erg += '{"path": "'+configSensor["gust"]+'","value":'+str(float(data["gust"]))+'},'
							if "rain" in data:
								Erg += '{"path": "'+configSensor["rain"]+'","value":'+str(float(data["rain"]))+'},'
							if "code" in data:
								Datet = str(data["time"])
								Datet = Datet[:10]+'T'+Datet[11:]+".000Z"
								#print(2,Datet)
								Erg += '{"path": "'+configSensor["code"]+'","value":"'+Datet+'"},'
								type_rtl = type_rtl + '.' + str(data["code"])
								
							SignalK = '{"updates":[{"$source":"OPsensors.RTL433.'+type_rtl+'","values":[ '
							SignalK +=Erg[0:-1]+']}]}\n'
							sock.sendto(SignalK.encode(), ('127.0.0.1', 55557))
							print(SignalK)
							sys.stdout.flush()
		
	retval = process.poll()
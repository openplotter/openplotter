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

import os, ujson, subprocess
#import pprint

class SK_settings:

	def __init__(self, conf):

		self.conf = conf
		self.setting_file = self.conf.home+'/.signalk/settings.json'

	def get(self):
		if os.path.isfile(self.setting_file):
			with open(self.setting_file) as data_file:
				self.data = ujson.load(data_file)
		else:
			self.data = {}
			print('Error: file ~/.signalk/settings.json does not exists')

		self.found = False	
		self.newdata = {}
		
		for j in self.data:	
			if 'pipedProviders' in self.data:
				for i in self.data['pipedProviders']:
					if i['id'] == 'OPkplex':
						self.found = True
						return self.found

				return self.found
				
	def set(self,activ):
		self.activ = activ

		if os.path.isfile(self.setting_file):
			with open(self.setting_file) as data_file:
				self.data = ujson.load(data_file)
		else:
			self.data = {}
			print('Error: file ~/.signalk/settings.json does not exists')

		self.found = False
		write = False	
		self.newdata = dict(self.data)
		
		self.newdata.pop('pipedProviders', None)
		dat = []
		
		if 'pipedProviders' in self.data:
			for i in self.data['pipedProviders']:
				if i['id'] == 'OPkplex':
					self.found = True
					if self.activ:
						dat.append(i)
					else:
						write = True
				else:
					dat.append(i)
					
			if not self.found and self.activ:
				dat.append({'enabled': True, 'id': 'OPkplex','pipeElements': [{'options': {'logging': False, 'type': 'NMEA0183', 'subOptions': {'host': 'localhost', 'type': 'tcp', 'port': '30330'}}, 'type': 'providers/simple'}]})
				write = True				
		
		self.newdata['pipedProviders'] = dat
		#pp = pprint.PrettyPrinter(indent=4)
		#pp.pprint(self.newdata)			
		if write: self.write_settings(self.newdata)
		
	def write_settings(self,data):
		data = ujson.dumps(data, indent=4, sort_keys=True)
		try:
			wififile = open(self.setting_file, 'w')
			wififile.write(data.replace('\/','/'))
			wififile.close()
		except: print('Error: error saving Signal K settings')
		
				

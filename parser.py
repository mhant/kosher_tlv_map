#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from HTMLParser import HTMLParser
import codecs
import urllib
import sys

class KosherParser(HTMLParser):
	in_td = False
	in_tr = False
	in_table = False
	table_data = []
	temp_row = []
	table_row = 0

	def handle_starttag(self, tag, attrs):
		if self.in_table and tag == 'td':
			self.in_td = True
		elif self.in_table and tag == 'tr':
			self.in_tr = True
			self.table_data.append([])
			# print 'new row' + str(len(self.table_data))
		elif tag == 'table':
			# print attrs
			for name, value in attrs:
				if name == 'class' and 't-b' in value:
					self.in_table = True

	def handle_data(self, data):
		if self.in_td:
			# print 'td'
			# self.table_data[self.table_row].append(data)
			if data:
				self.temp_row.append(data)
			# print 'new cell ' + str(len(self.table_data[self.table_row])) + ' for row ' + str(self.table_row)
		# elif self.in_tr:
			# print 'tr'

	def handle_endtag(self, tag):
		if self.in_table and tag == 'td':
			self.in_td = False
		elif self.in_table and tag == 'tr':
			self.in_tr = False
			if len(self.temp_row) > 0:
				self.table_data[self.table_row] = self.temp_row
				self.temp_row = []
				self.table_row = self.table_row + 1
		elif tag == 'table':
			self.in_table = False

if len(sys.argv) < 2:
	print "Need google map key!"
	sys.exit(22);
goe_code_url_post = '&key=' + sys.argv[1]
goe_code_url_pre = 'https://maps.googleapis.com/maps/api/geocode/json?address='
kosher_url = "http://www.rabanut.co.il/Sapakim/show/comp/comps.aspx"
r = requests.get(kosher_url)
r.encoding = 'utf-8'
parser = KosherParser()
redux_text = r.text.replace('&','+').replace('\t','')
parser.feed(redux_text)
final_list = []
tel_aviv_u = ' תל אביב'
tel_aviv = tel_aviv_u.decode('utf8')
coords = {}
count = 0
with codecs.open("addresses_bool.js", 'wb',  'utf-8') as f:
	f.write("var addresses = [");
	for rest in parser.table_data:
		table_len = len(rest)
		if (table_len == 6 or table_len == 5):
			count = count + 1

			name = rest[0].replace("'","")
			type = rest[1].replace("'","")
			kosher_type = rest[2].replace("'","")
			place = 5
			if table_len == 5:
				place = 4
			kosher_exp = rest[place].replace("'","")
			location = rest[3] + tel_aviv
			location = location.replace("'","")
			address = rest[3].replace("'","")

			#now check if this is on our correction list


			f.write("{\n")
			# name of place
			f.write("'rest_name':'")

			f.write(name)
			f.write("',\n")
			# type of place
			f.write("'rest_type':'")

			f.write(type)
			f.write("',\n")
			# type of koshrut (meat, milky, both)
			f.write("'kosher_type':'")

			f.write(kosher_type)
			f.write("',\n")
			# kashrut expiration
			f.write("'kosher_exp':'")
			f.write(kosher_exp)
			f.write("',\n")
			# street address
			f.write("'rest_addr':'")
			f.write(address)
			f.write("',\n")
			geo_url = goe_code_url_pre + urllib.quote(location.replace("'","").encode('utf-8')) + goe_code_url_post
			gr = requests.get(geo_url)
			json = gr.json()
			if ('results' in json and len(json['results']) > 0):
				lat = json['results'][0]['geometry']['location']['lat']
				lng = json['results'][0]['geometry']['location']['lng']


				for i in range( 0, 1000 ):
					key = str(lat) + "_" + str(lng)
					if key in coords: #something already exists at that lat_lng. offset it and try again
						lat += 0.00003
						lng += 0.00003
					else: #noone at that position yet.
						coords[key] = 1
						break

				f.write("'lat':'" + str(lat) + "',\n")
				f.write("'lng':'" + str(lng) + "'")
			else:
				f.write("//No results\n")
			f.write("\n},")
			# f.write(str(counter) + " ============================================\n")
			#
			# location = rest[3] + tel_aviv
			# f.write( location)
			#
			# f.write( "\n" + goe_code_url_pre)
			# f.write( urllib.quote(location.replace("'","").encode('utf-8')))
			# f.write( goe_code_url_post)
			# f.write( "\n============================================\n")
	f.write("];");
# 		final_list.append(rest)
# with codecs.open("addresses.js", 'wb',  'utf-8') as f:
# 	f.write("var addresses = [");
# 	for rest in final_list:
# 		if len(rest) == 5:
# 			f.write("{\n")
# 			f.write("'rest_name':'")
# 			name = rest[0].replace("'","")
# 			f.write(name)
# 			f.write("',\n")
# 			#f.write("'rest_type':'" +  rest[1].encode("UTF-16") + "',\n")
# 			#f.write("'kosher_type':'" +  rest[2].encode("UTF-16") + "',\n")
# 			f.write("'rest_addr':'")
# 			address = rest[3].replace("'","")
# 			f.write(address)
# 			f.write("'\n},")
# 			#f.write("'rest_addr':'" +  rest[3].encode("UTF-16") + "',\n")
# 			#f.write("'rest_phone':'" +  rest[4].encode("UTF-16") + "',\n")
# 			#f.write("'expire_kosher':'" +  rest[3].encode("UTF-16") + "'\n},")
# 	f.write("];");

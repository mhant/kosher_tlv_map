#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import requests
from html.parser import HTMLParser
import codecs
import urllib
import urllib.parse
from urllib.parse import quote   #now needed in python 3
from urllib.parse import urlparse
from urllib.parse import parse_qs
import re
import datetime

from correction_addresses import *



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
		elif tag == 'a' and self.in_td and self.in_table and self.in_tr:
			for name, value in attrs:
				if name == 'href':
					parsed_url = urlparse(value)
					item_id = parse_qs(parsed_url.query)['id'][0]
					# need to parse out the int id because we get junk in there
					item_id_int = re.search(r'\d+', item_id).group()
					self.temp_row.append(item_id_int)

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
	print("Need google map key!")
	sys.exit(22);

start_time = datetime.datetime.now();
goe_code_url_post = '&key=' + sys.argv[1]
goe_code_url_pre = 'https://maps.googleapis.com/maps/api/geocode/json?address='
kosher_url = "http://www.rabanut.co.il/Sapakim/show/comp/comps.aspx"
r = requests.get(kosher_url)
r.encoding = 'utf-8'
parser = KosherParser()
redux_text = r.text.replace('&','+').replace('\t','')
parser.feed(redux_text)
final_list = []
tel_aviv_u = ' תל אביב יפו'
tel_aviv = tel_aviv_u # in python 3 all strings are decoded. no need for this :tel_aviv_u.decode('utf8')
coords = {}
typesToIgnore = ['בית ספר לבישול', 'בתי אבות','בתי חולים', 'מפעל', 'אולמות אירועים'];
ignored = 0; #r_type was in typesToIgnore
corrected = 0; #was in the corrections list
hidden = 0;  #was in teh corrections list to be hidden.

count = 0
with codecs.open("corrected_addresses_bool.js", 'wb',  'utf-8') as f:
	now = datetime.datetime.now()
	f.write("var parser_run_date = \""+ now.strftime("%d-%m-%y %H:%M") +"\"\n");
	f.write("var addresses = [");
	for rest in parser.table_data:
		table_len = len(rest)
		# make sure we have an ID and array of 6 or 7 (maybe only 6?)
		# watch out for 0 size rows in the array
		if (table_len >= 6 and table_len <= 7 and rest[0].isdigit()):
			count = count + 1

			name = rest[1].replace("'","")
			rest_id = rest[0].replace("'","")
			r_type = rest[2].replace("'","")
			kosher_type = rest[3].replace("'","")
			kosher_exp = rest[table_len-1].replace("'","")
			location = rest[4] + tel_aviv
			location = location.replace("'","")
			address = rest[4].replace("'","")

			#check if we should ignore this type
			if ( r_type in typesToIgnore ):
				ignored += 1;
				continue;

			#now check if this is on our correction list
			break1=False
			for place in correction_addresses:
				if( place['orig_rest_name'] == name and place['orig_rest_addr'] == address ):
					if( place['mod_type'] != 'hide' ):
						name = place['rest_name']
						address = place['rest_addr']
						location = address + tel_aviv
						location = location.replace("'","")
						kosher_type = place['kosher_type']
						corrected += 1;
						break #from the correction loop
					else:
						hidden += 1;
						break1=True
						break #out of the place loop
			if( break1 ):
				continue #next in the rest loop


			f.write("{\n")
			# id for rest
			f.write("'rest_id':'")
			f.write(rest_id)
			f.write("',\n")
			# gen the url for the rabanut item page
			rab_url = 'http://www.rabanut.co.il/show_item.asp?itemId=185&levelId=60055&itemType=0&id=' + rest_id + '&xsltemplate=1'
			f.write("'rest_rab_url':'")
			f.write(rab_url)
			f.write("',\n")

			# add the kashrut type for later iterations
			f.write("'kosher_list_type':'")
			f.write("rabanut")
			f.write("',\n")

			# name of place
			f.write("'rest_name':'")
			f.write(name)
			f.write("',\n")

			# type of place
			f.write("'rest_type':'")

			f.write(r_type)
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


			#geo_url = goe_code_url_pre + urllib.parse.quote(location.replace("'","").encode('utf-8')) + goe_code_url_post
			geo_url = goe_code_url_pre + urllib.parse.quote(location.encode('utf-8')) + goe_code_url_post
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
				f.write("//No results. has the google key been used up?\n")
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
	f.write("];\n\n");
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

	f.write("var num_ignored="+str(ignored)+";\n");
	f.write("var num_corrected="+str(corrected)+";\n");
	f.write("var num_hidden="+str(hidden)+";\n");

	end_time = datetime.datetime.now();
	f.write("var parser_duration_seconds="+str((end_time-start_time).total_seconds())+";\n");



#now output a file of the corrections.
with codecs.open("concise_corrected_addresses_bool.js", 'wb',  'utf-8') as f:
	f.write("var addresses = [");
	for address in correction_addresses:
			f.write("{\n")

			# name of place
			f.write("'orig_rest_name':'")

			f.write(address['orig_rest_name'])
			f.write("',\n")


			# type of place
			f.write("'orig_rest_type':'")

			f.write(address['orig_rest_type'])
			f.write("',\n")


			# type of koshrut (meat, milky, both)
			f.write("'orig_kosher_type':'")

			f.write(address['orig_kosher_type'])
			f.write("',\n")



			# street address
			f.write("'orig_rest_addr':'")
			f.write(address['orig_rest_addr'])
			f.write("',\n")





			# name of place
			f.write("'rest_name':'")

			f.write(address['rest_name'])
			f.write("',\n")


			# type of place
			f.write("'rest_type':'")

			f.write(address['rest_type'])
			f.write("',\n")


			# type of koshrut (meat, milky, both)
			f.write("'kosher_type':'")

			f.write(address['kosher_type'])
			f.write("',\n")


			# street address
			f.write("'rest_addr':'")
			f.write(address['rest_addr'])
			f.write("',\n")

			# street address
			f.write("'mod_type':'")
			f.write(address['mod_type'])
			f.write("',\n")

			# street address
			f.write("'reason':'")
			f.write(address['reason'])
			f.write("',\n")

			# street address
			f.write("'id':'")
			f.write(address['id'])
			f.write("'\n},")


	f.write("];\n");

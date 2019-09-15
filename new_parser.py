#!/usr/bin/env python
# -*- coding: utf-8 -*-
from html.parser import HTMLParser
import datetime
import requests
import pprint
import codecs

class KosherParser(HTMLParser):
    # count of total kosher items
    counter = 0
    # this allows us to close once we exit the kosher item div
    div_counter = 0
    in_it = False
    table_data = []
    k_item = {}
    in_post_title = False
    in_business_type = False
    in_wrap_address = False

    def handle_starttag(self, tag, attrs):
        # print(attrs)
        # if we're in a kosher obj
        if self.in_it:
            # we only really need the first attribute right now
            if (len(attrs) > 0):
                attr = attrs[0]
                if (len(attr) > 0):
                    if(attr[0] == 'href'):
                        self.k_item['url'] = attr[1]
                    elif (len(attr) > 0):
                        if(attr[1] == 'post_title'):
                            self.in_post_title = True;
                        if(attr[1] == 'business_type'):
                            self.in_business_type = True
                        if(attr[1] == 'wrap_address'):
                            self.in_wrap_address = True
        # when we start a kosher item, flip bool
        if (tag == 'div'):
            for attr in attrs:
                # print(attr)
                # print(type(attr))
                if ('column post_col kosher_item' in attr):
                    self.in_it = True
                    self.counter = self.counter + 1
                    # print(self.counter)
            if self.in_it:
                self.div_counter = self.div_counter + 1
    def handle_data(self, data):
        if self.in_post_title:
            # print("title is: " + data)
            self.k_item['name'] = data
            self.in_post_title = False;
        if self.in_business_type:
            self.k_item['rest_type'] = data
            self.in_business_type = False;
        if self.in_wrap_address:
            self.k_item['address'] = data
            self.in_wrap_address = False;

    def handle_endtag(self, tag):
        if tag == 'div':
            if self.in_it:
                if self.div_counter == 1:
                    self.table_data.append(self.k_item)
                    self.k_item = {}
                    self.in_it = False
                self.div_counter = self.div_counter - 1

start_time = datetime.datetime.now();
kosher_url = "https://rabanut.co.il/%D7%97%D7%99%D7%A4%D7%95%D7%A9-%D7%A2%D7%A1%D7%A7%D7%99%D7%9D-%D7%9B%D7%A9%D7%A8%D7%99%D7%9D/page/"
# page over all pages
for i in range(1,15):
    url = kosher_url + str(i)
    r = requests.get(url)
    r.encoding = 'utf-8'
    parser = KosherParser()
    parser.feed(r.text)
    print(str(len(parser.table_data)))
typesToIgnore = ['בית ספר לבישול', 'בתי אבות','בתי חולים', 'מפעל', 'אולמות אירועים']
with codecs.open("new_addresses_bool.js", 'wb',  'utf-8') as f:
    count = 0
    now = datetime.datetime.now()
    f.write("var parser_run_date = \""+ now.strftime("%d-%m-%y %H:%M") +"\"\n")
    f.write("var addresses = [")
    for rest in parser.table_data:
        count = count + 1
        name = rest['name'].replace("'","")
        rest_id = str(count)
        r_type = rest['rest_type']
        address = '' if 'address' not in rest else rest['address']
        rab_url = rest['url']
        if ( r_type in typesToIgnore ):
            ignored += 1;
            continue;
        f.write("{\n")
        # id for rest
        f.write("'rest_id':'")
        f.write(rest_id)
        f.write("',\n")

        # gen the url for the rabanut item page
        f.write("'rest_rab_url':'")
        f.write(rab_url)
        f.write("',\n")

        # name of place
        f.write("'rest_name':'")
        f.write(name)
        f.write("',\n")

        # type of place
        f.write("'rest_type':'")
        f.write(r_type)
        f.write("',\n")

        # street address
        f.write("'rest_addr':'")
        f.write(address)
        f.write("',\n")

        f.write("];\n\n");

    end_time = datetime.datetime.now();
    f.write("var parser_duration_seconds="+str((end_time-start_time).total_seconds())+";\n")

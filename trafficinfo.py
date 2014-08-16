#!/usr/bin/env python

from bs4 import BeautifulSoup
from urllib2 import urlopen
import sys
import smtplib
import myconfig_gmail
import myphonenumber
import HERE_credentials


HERE_API_HTML = 'http://route.cit.api.here.com/routing/7.2/calculateroute.json' \
'?app_id={0}&app_code={1}' \
'&waypoint0=geo!{2},{3}&waypoint1=geo!{4},{5}' \
'&mode=fastest;car;traffic:enabled'

def read_api(position1, position2):
# Read the route API from HERE using our credentials
# and return the first paragraph in text
# It corresponds to the route information between
# position 1 and position 2
	myhtml = HERE_API_HTML.format(
	HERE_credentials.App_Keys['App_id'], HERE_credentials.App_Keys['App_Code'],
	position1[0], position1[1], position2[0], position2[1])
	print myhtml
	mysoup = BeautifulSoup( urlopen(myhtml).read() )
	
	mytxt = mysoup.find('p').get_text()
	return mytxt

def extract_time(HEREapitxt):
# Extract time information from results of an API request
# on HERE.com. The results are converted into float numbers
# Results (resp.) in m, sec and sec.
	myindex_beg = HEREapitxt.find('summary')
	myindex_end = HEREapitxt[myindex_beg:].find('}')
	element_keys = HEREapitxt[myindex_beg:myindex_beg+myindex_end+1].split('"')
	ii = 0
	print myindex_beg, myindex_end, element_keys
	while element_keys[ii] != 'distance':
		ii += 1
	try:
		distance = float(element_keys[ii+1][1:-1])
		trafficTime = float(element_keys[ii+3][1:-1])
		baseTime = float(element_keys[ii+5][1:-1])
	except:
		"Error extract_time: Could not find times."
		sys.exit(1)

	return distance, trafficTime, baseTime


def send_text(msg):                                                  
# This is set up to send a text message to Virgin Mobile
# phone number
    fromaddr = "Traffic Info"
    toaddrs = myphonenumber.phone_number + "@vmobl.com"
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()   # used for encryption
    server.login(myconfig_gmail.email['username'], myconfig_gmail.email['password'])
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()



#!/usr/bin/env python

from bs4 import BeautifulSoup
from urllib2 import urlopen
import sys
import smtplib
import time

import myconfig_gmail
import HERE_credentials


HERE_API_HTML = 'http://route.cit.api.here.com/routing/7.2/calculateroute.json' \
'?app_id={0}&app_code={1}' \
'&waypoint0=geo!{2},{3}&waypoint1=geo!{4},{5}' \
'&mode=shortest;car;traffic:enabled'
ALTFACTOR = 1.1	# Factor to advantage Mopac over alternative route
PHONENBLIST = 'phonenumbers.txt'
TXTEMAILEXT = dict(
	Virgin = '@vmobl.com',
	ATT = '@txt.att.net'
)

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
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()   # used for encryption
	server.login(myconfig_gmail.email['username'], myconfig_gmail.email['password'])
	phonelistfile = open(PHONENBLIST, 'r')
	for myphnb in phonelistfile:
		phnb = myphnb.split()
		toaddrs = phnb[0] + TXTEMAILEXT[phnb[1]]
		server.sendmail(fromaddr, toaddrs, msg)
	server.quit()


def check_dist(ref_dist, web_dist):
# Check distance obtained from request does not diverge too much from
# reference distance
	assert (abs(int(ref_dist) - int(web_dist))/100) == 0, \
	'Error in check_dist between {0} and {1}'.format(str(ref_dist), str(web_dist))


def time_route(filename):
# Return travel time in traffic condition
# over each portion of a route
	try:
		myfile = open(filename, 'r')
	except:
		print 'Error time_route: could not open {0}'.format(filename)
		sys.exit(1)

	TotalTimeperParts = []
	mylines = myfile.readlines()
	indexln = 1	
	indexPart = 2
	mytime = 0.

	while mylines[indexln+1].split()[0] != 'End':
		if mylines[indexln+1].split()[0] == 'Part' + str(indexPart):
			TotalTimeperParts.append(mytime)
			mytime = 0.
			indexln += 2
			indexPart += 1
		mypositions = []
		mypositions.append(mylines[indexln].split()[0:2])
		mypositions.append(mylines[indexln+1].split()[0:2])
		refdist = int( mylines[indexln+1].split()[2] )
		# Clean-up potential spurious comma in positions
		for ii in range(2):
			for jj in range(2):
				try:
					float(mypositions[ii][jj])
				except:
					mypositions[ii][jj] = mypositions[ii][jj][:-1]

		dist, trafficTime, baseTime = extract_time( read_api(mypositions[0], mypositions[1]) )
		check_dist(refdist, dist)
		mytime += trafficTime
		indexln += 1
	TotalTimeperParts.append(mytime)	# Don't miss the last time
	
	myfile.close()

	return TotalTimeperParts


def route_comparison(direction):
# Scrape info on website and compare main and alt routes
# over each portions defined 
	if direction == 'NB':
		MOPAC = 'NB_Mopac.py'
		ALT = 'NB_Alt.py'
	elif direction == 'SB':
		MOPAC = 'SB_Mopac.py'
		ALT = 'SB_Alt.py'
	else:
		print "Error route_comparison: direction selected does not exist"
		sys.exit(1)

	TimesMopac = time_route(MOPAC)
	TimesAlt = time_route(ALT)

	TakeMopac = []
	for ii in range(len(TimesMopac)):
		a = TimesMopac[ii]
		b = TimesAlt[ii]
		if a < ALTFACTOR*b:	TakeMopac.append(True)
		else:	TakeMopac.append(False)

	return TakeMopac


def generate_msg(direction, TakeMopac):
# Decide what route to take depending on the driving times obtained
	if direction == 'NB':
		msgfile = open('NB_mymsg.txt', 'r')
		mylines = msgfile.readlines()
		msgfile.close()

		if TakeMopac[0]*TakeMopac[1] == 1:
			msg = mylines[0]
			if TakeMopac[2]*TakeMopac[3]*TakeMopac[4] == 1:	return mylines[1]
			else:
				if TakeMopac[2] == 0:	msg = msg + mylines[4]
				if TakeMopac[3] == 0:	msg = msg + mylines[5]
				if TakeMopac[4] == 0:	msg = msg + mylines[6]
		elif TakeMopac[1] == 1:	
			msg = mylines[2]
			if TakeMopac[2] == 0:	msg = msg + mylines[4]
			if TakeMopac[3] == 0:	msg = msg + mylines[5]
			if TakeMopac[4] == 0:	msg = msg + mylines[6]
		else:
			if TakeMopac[2] == 1:	
				msg = mylines[3]
				if TakeMopac[3] == 0:	msg = msg + mylines[5]
				if TakeMopac[4] == 0:	msg = msg + mylines[6]
			elif TakeMopac[3] == 1:	
				msg = mylines[7]
				if TakeMopac[4] == 0:	msg = msg + mylines[6]
			else:
				return mylines[8]

	if direction == 'SB':
		msgfile = open('SB_mymsg.txt', 'r')
		mylines = msgfile.readlines()
		msgfile.close()

		if TakeMopac[0]*TakeMopac[1] == 1:
			msg = mylines[0]
			if TakeMopac[2]*TakeMopac[3]*TakeMopac[4] == 1:	return mylines[1]
			else:
				if TakeMopac[2] == 0:	msg = msg + mylines[4]
				if TakeMopac[3] == 0:	msg = msg + mylines[5]
				if TakeMopac[4] == 0:	msg = msg + mylines[6]
		elif TakeMopac[1] == 1:	
			msg = mylines[2]
			if TakeMopac[2] == 0:	msg = msg + mylines[4]
			if TakeMopac[3] == 0:	msg = msg + mylines[5]
			if TakeMopac[4] == 0:	msg = msg + mylines[6]
		else:
			if TakeMopac[2] == 1:	
				msg = mylines[3]
				if TakeMopac[3] == 0:	msg = msg + mylines[5]
				if TakeMopac[4] == 0:	msg = msg + mylines[6]
			elif TakeMopac[3] == 1:	
				msg = mylines[7]
				if TakeMopac[4] == 0:	msg = msg + mylines[6]
			else:
				return mylines[8]

	else:
		print "Error generate_msg: direction selected does not exist"
		sys.exit(1)

	return msg


def wait_tilnextrun():
# Code runs M through F at 8:00am(NB), 8:30am(SB),
# 2:45pm(NB) and 3:15pm(SB)
# return the direction of the next computation
	daytoday = datetime.today()
	dt = []
	if daytoday.weekday() < 5:
		date1 = datime(daytoday.year, daytoday.month, daytoday.day, 7, 30); dt.append((date1 - daytoday).total_seconds())
		date2 = datime(daytoday.year, daytoday.month, daytoday.day, 8, 30); dt.append((date2 - daytoday).total_seconds())
		date3 = datime(daytoday.year, daytoday.month, daytoday.day, 14, 30); dt.append((date3 - daytoday).total_seconds())
		date4 = datime(daytoday.year, daytoday.month, daytoday.day, 15, 15); dt.append((date4 - daytoday).total_seconds())
		for timeleft, myindex in zip(dt, range(4)):
			if timeleft > 0.:
				time.sleep(timeleft)
				if index % 2 == 0:	return 'NB'
				else:	return 'SB'
		if daytoday.weekday() < 4:
			timeleft = (datime(daytoday.year, daytoday.month, daytoday.day+1, 8) - daytoday).total_seconds()
		else:
			timeleft = (datime(daytoday.year, daytoday.month, daytoday.day+3, 8) - daytoday).total_seconds()
		time.sleep(timeleft)

	elif daytoday.weekday() == 5:	
		timeleft = (datime(daytoday.year, daytoday.month, daytoday.day+2, 8) - daytoday).total_seconds()
		time.sleep(timeleft)
		return 'NB'

	elif daytoday.weekday() == 6:	
		timeleft = (datime(daytoday.year, daytoday.month, daytoday.day+1, 8) - daytoday).total_seconds()
		time.sleep(timeleft)
		return 'NB'

	else:
		print "Error wait_tilnextrun: Could not find what day we are today..."
		sys.exit(1)


if __name__ == "__main__":
	while True:
		direction = wait_tilnextrun()	# Only run between M and F
		# First time prior beginning of trip
		msg1 = generate_msg(direction, route_comparison(direction))
		send_text(msg1)
		# Second time 15 min after beginning of trip
		time.sleep(900)
		msg2 = generate_msg(direction, route_comparison(direction))
		if msg1 != msg2:	send_text(msg2)

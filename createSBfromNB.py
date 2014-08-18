#!/usr/bin/env python

import sys

def createSB(filenameNB, filenameSB):
	NBfile = open(filenameNB, 'r')
	NBlines = NBfile.readlines()
	NBfile.close()

	SBlines = []
	indexparts = 1
	for ii in range(len(NBlines)-1, 0, -1):
		if NBlines[ii][0] == 'E' or NBlines[ii][0] == 'P':	
			SBlines.append('Part' + str(indexparts))
			indexparts += 1
		else:
			SBlines.append(NBlines[ii])
	SBlines.append('End')

	SBlines2 = []
	dist = ''
	for ln1 in SBlines:
		if ln1[0] == 'E' or ln1[0] == 'P':
			SBlines2.append(ln1)
		else:
			lnsplt = ln1.split()
			ln2 = lnsplt[:2]
			if ln2[1][-1] != ',':	ln2[1] = ln2[1] + ','
			ln2.append(dist)
			SBlines2.append(' '.join(ln2))
			try:
				dist = ln1.split()[2]
			except:
				dist = ''

	SBfile = open(filenameSB, 'w')
	for myline in SBlines2:
		SBfile.write('{0}\n'.format(myline))
	SBfile.close()


if __name__ == "__main__":
	try:
		fileNB = sys.argv[1]
		fileSB = sys.argv[2]
	except:
		print 'Error -- Usage: {0} filenameNB filenameSB'.format(sys.argv[0])

	createSB(fileNB, fileSB)

#!/usr/bin/python

import httplib
import json
import csv
import os
import sys
import time
import urllib
import datetime
import uuid

APPLICATION_ID = "4R03PRP8btiY00gdKqkl7lIlJyj6HYN7QFeodrfR"
MASTER_KEY = "6NtABNvHhiAz9xRUQCXMeElqhqgJQp1wItcQB9AC" #Master Key

skip = 0 # Skip these many rows, used in skip = skip_count*limit
limit = 10 #limit number of rows per call - Max is 1000

def getData(app_id, api_endpoint, master_key=None, limit=1000, order=None, skip=None, filter_json=None, api_version="parse"):
	con = httplib.HTTPConnection('127.0.0.1', 1337)
	con.connect()

	header_dict = {
		'X-Parse-Application-Id': app_id,
		'X-Parse-Master-Key': master_key
	}
	
	params_dict = {}
	if order is not None:
		params_dict['order'] = order
	if limit is not None:
		params_dict['limit'] = limit
	if skip is not None:
		params_dict['skip'] = skip
	if filter_json is not None:
		params_dict['where'] = filter_json

	params = urllib.urlencode(params_dict)
	con.request('GET', '/%s/%s?%s' % (api_version, api_endpoint, params), '', header_dict)

	try:
		response = json.loads(con.getresponse().read())
	except Exception, e:
		response = None
		raise e

	return response

def PrepareBoth_CSV_JSON(class_list):
	print "*** Requesting...  ***\n"

	#class_list = CLASSES.split(",") #For multiple classes!
	#DEFAULT_CLASSES = {'User': 'users', 'Role': 'roles', 'File': 'files', 'Events': 'events', 'Installation': 'installations'}
	DEFAULT_CLASSES = {}
	
	RandomName_ByHostNTime = str(uuid.uuid1())
	json_file_path = os.getcwd()+"/download/"+RandomName_ByHostNTime
	if not os.path.exists(json_file_path):
		os.makedirs(json_file_path)
	
	print str(class_list)
	for classname in class_list:
		results = {'results': []}
		object_count = 0
		skip_count = 0

		if classname not in DEFAULT_CLASSES.keys():
			endpoint = '%s/%s' % ('classes', classname)
		else:
			endpoint = DEFAULT_CLASSES[classname]

		sys.stdout.write(' Fetching %s table data - ' % classname)
		sys.stdout.flush()

		while True:
			startTimer = time.clock()
			skip = skip_count*limit

			response = getData(APPLICATION_ID, endpoint, master_key=MASTER_KEY, limit = limit, skip = skip)
			print "\n\n'"+classname+"':\n"+str(response)+"\n\n\n"
			if 'results' in response.keys() and len(response['results']) > 0:
				object_count += len(response['results'])
				skip_count = skip_count+1
				results['results'].extend(response['results'])
			else:
				parse_done = time.clock() - startTimer
				print ' Got: %.4f records in %.4f secs\n' % (object_count, parse_done)
				break

		with open(os.path.join(json_file_path, '%s.json' % classname), 'w') as json_file:
			json_file.write(json.dumps(results, indent=4, separators=(',', ': ')))

		#print 'Generating csv... '
		#
		#with open(os.path.join(json_file_path, '%s.json' % classname), 'r') as json_file:
		#
		#	data = json.load(json_file)
		#	f = csv.writer(open(os.path.join(json_file_path, '%s.csv' % classname), 'w'))
		#	f.writerow(data["results"][0].keys())
		#	for x in data["results"]:
		#		f.writerow(x.values())
		#	print " CSV Generated... \n"
		os.system("zip -r -j "+json_file_path+"/"+RandomName_ByHostNTime+".zip "+json_file_path)
	return RandomName_ByHostNTime

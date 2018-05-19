#!/usr/bin/python

import httplib
import json
import csv
import os
import sys
import time
import urllib
import datetime

APPLICATION_ID = "4R03PRP8btiY00gdKqkl7lIlJyj6HYN7QFeodrfR"
MASTER_KEY = "6NtABNvHhiAz9xRUQCXMeElqhqgJQp1wItcQB9AC" #Master Key
skip = 0 # Skip these many rows, used in skip = skip_count*limit
limit = 10 #limit number of rows per call - Max is 1000

def getAllClassNameData_ByWill(app_id, api_endpoint="schemas", master_key=None, limit=1000, order=None, skip=None, filter_json=None, api_version="parse"):
	con = httplib.HTTPConnection('127.0.0.1', 1337)
	con.connect()
	header_dict = {
		'X-Parse-Application-Id': app_id,
		'X-Parse-Master-Key': master_key
	}	
	con.request('GET', '/%s/%s' % (api_version, api_endpoint), '', header_dict)
	#con.request('GET', '/parse/schemas' , '', header_dict)
	try:
		response = json.loads(con.getresponse().read())			#Load the response as JSON		
	    
	except Exception, e:
		response = None
		raise e

	return response

def findkeys(node, kv):
	if isinstance(node, list):
		for i in node:
			for x in findkeys(i, kv):
				yield x
	elif isinstance(node, dict):
		if kv in node:
			yield node[kv]
		for j in node.values():
			for x in findkeys(j, kv):
				yield x
#print list(findkeys(d, 'id'))

def AllClassList():
	print "*** Requesting ...  ***\n"

	json_file_path = os.getcwd()	
	ReturnClassList = []
	object_count = 0
	done = False
	sys.stdout.write(' Fetching %s table data - schemas')
	sys.stdout.flush()

	while True:
		startTimer = time.clock()
		response = getAllClassNameData_ByWill(APPLICATION_ID, api_endpoint='schemas', master_key=MASTER_KEY, limit=limit, skip = 0)
		if 'results' in response.keys() and len(response['results']) > 0 and done==False:
			object_count += len(response['results'])
			ReturnClassList.extend(findkeys(response['results'], 'className'))
			done=True
			print "\n--New My Class List:"+str(ReturnClassList)
		elif done==True:
			parse_done = time.clock() - startTimer
			print ' Got: %.4f records in %.4f secs\n' % (object_count, parse_done)
			break
		else:
			print "*** Requesting Again ...  ***\n"
	return ReturnClassList

def ClassNFieldList_SpecificClass():
	print "*** Requesting ...  ***\n"

	json_file_path = os.getcwd()	
	ReturnClassList = []
	object_count = 0
	done = False
	sys.stdout.write(' Fetching %s table data - schemas')
	sys.stdout.flush()

	while True:
		startTimer = time.clock()
		response = getAllClassNameData_ByWill(APPLICATION_ID, api_endpoint='schemas', master_key=MASTER_KEY, limit=limit, skip = 0)

		if 'results' in response.keys() and len(response['results']) > 0 and done==False:
			#return(response['results'])
			object_count += len(response['results'])
			
			
			for idx, dict in enumerate(response['results']):
				oput = {}
				oput["className"] = dict["className"]
				oput["fields"] = dict["fields"].keys()
				oput["type"]=[]
				oput["type"].extend(findkeys(dict["fields"], 'type'))
				oput["targetClass"]=[]
				oput["targetClass"].extend(findkeys(dict["fields"], 'targetClass'))
				print str(oput)
				ReturnClassList.append(oput)
			
			done=True
			print "\n--New My Class List:"+str(ReturnClassList)
		elif done==True:
			parse_done = time.clock() - startTimer
			print ' Got: %.4f records in %.4f secs\n' % (object_count, parse_done)
			break
		else:
			print "*** Requesting Again ...  ***\n"
	return ReturnClassList

#if __name__ == '__main__':
#	try:
#		a= ClassNFieldList_SpecificClass()
#		print a[0]["className"]
#		print a[1]["className"]
#		print a[0]["fields"]
#		print a[1]["fields"]
#		print "length"+str(len(a))
#	except Exception, e:
#		raise e

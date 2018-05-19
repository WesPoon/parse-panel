import httplib
import json
import csv
import os
import sys
import time
import urllib
import datetime
import ssl
import requests

APPLICATION_ID = "4R03PRP8btiY00gdKqkl7lIlJyj6HYN7QFeodrfR"
MASTER_KEY = "6NtABNvHhiAz9xRUQCXMeElqhqgJQp1wItcQB9AC" #Master Key
skip = 0 # Skip these many rows, used in skip = skip_count*limit
limit = 10 #limit number of rows per call - Max is 1000

def getUserClassElements(classname):
	
	con = httplib.HTTPConnection('127.0.0.1',1337)
	con.connect()
	header_dict = {
		'X-Parse-Application-Id': APPLICATION_ID,
		'X-Parse-Master-Key': MASTER_KEY
	}	
	con.request('GET', '/parse/users/', '', header_dict)
	try:
		response = json.loads(con.getresponse().read())
	except Exception, e:
		response = None
		print e
		raise e
	con.close()
	
	return response


def ClassNFieldList_SpecificUserClass():
	print "*** Requesting User Class...  ***\n"

	json_file_path = os.getcwd()	
	ReturnClassList = []
	object_count = 0
	done = False
	sys.stdout.write(' Fetching %s User table data - schemas')
	sys.stdout.flush()

	while True:
		startTimer = time.clock()
		response = getUserClassElements('User')
		
		if 'results' in response.keys() and len(response['results']) > 0 and done==False:
			#return(response['results'])
			object_count += len(response['results'])
			print response['results']
			for idx, dict in enumerate(response['results']):
				oput = {}
				#oput["userame"] = dict["username"]
				oput["objectId"] = dict["objectId"]	
				post_headers = {"X-Parse-Application-Id":APPLICATION_ID,"X-Parse-Master-Key":MASTER_KEY,"Content-Type": "application/json"}
				post_payload = {"count": 5}
				put_response = requests.put('http://127.0.0.1/parse/users/'+oput["objectId"], data=json.dumps(post_payload) , headers=post_headers)
				print put_response.content
				ReturnClassList.append(oput)

			done=True
			print "\n--New User Class List:"+str(ReturnClassList)
		elif done==True:
			parse_done = time.clock() - startTimer
			print ' Got: %.4f records in %.4f secs\n' % (object_count, parse_done)
			break
		else:
			print "*** Requesting User Class Again ...  ***\n"
	return ReturnClassList


UserClassFieldList = ClassNFieldList_SpecificUserClass()
post_payload = {}












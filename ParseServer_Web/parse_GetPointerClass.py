import httplib
import json
import csv
import os
import sys
import time
import urllib
import datetime
import ssl

APPLICATION_ID = "4R03PRP8btiY00gdKqkl7lIlJyj6HYN7QFeodrfR"
MASTER_KEY = "6NtABNvHhiAz9xRUQCXMeElqhqgJQp1wItcQB9AC" #Master Key
skip = 0 # Skip these many rows, used in skip = skip_count*limit
limit = 10 #limit number of rows per call - Max is 1000

	
def getPointerClassElements(classname):
	
	con = httplib.HTTPConnection('127.0.0.1',1337)
	con.connect()
	header_dict = {
		'X-Parse-Application-Id': APPLICATION_ID,
		'X-Parse-Master-Key': MASTER_KEY
	}	
	con.request('GET', '/parse/classes/'+classname, '', header_dict)
	try:
		response = json.loads(con.getresponse().read())
	except Exception, e:
		response = None
		print e
		raise e
	con.close()
	return response
	
def ClassNFieldList_SpecificPointerClass(classname):
	print "*** Requesting Pointer Class...  ***\n"

	json_file_path = os.getcwd()	
	ReturnClassList = []
	object_count = 0
	done = False
	sys.stdout.write(' Fetching %s pointer table data - schemas')
	sys.stdout.flush()

	while True:
		startTimer = time.clock()
		response = getPointerClassElements(classname)

		if 'results' in response.keys() and len(response['results']) > 0 and done==False:
			#return(response['results'])
			object_count += len(response['results'])
			
			
			for idx, dict in enumerate(response['results']):
				oput = {}
				oput["Name"] = dict["Name"]
				oput["objectId"] = dict["objectId"]
				#oput["type"]=[]
				#oput["type"].extend(findkeys(dict["fields"], 'type'))
				#oput["targetClass"]=[]
				#oput["targetClass"].extend(findkeys(dict["fields"], 'targetClass'))
				print str(oput)
				ReturnClassList.append(oput)
			
			done=True
			print "\n--New Pointer Class List:"+str(ReturnClassList)
		elif done==True:
			parse_done = time.clock() - startTimer
			print ' Got: %.4f records in %.4f secs\n' % (object_count, parse_done)
			break
		else:
			print "*** Requesting Pointer Class Again ...  ***\n"
	return ReturnClassList
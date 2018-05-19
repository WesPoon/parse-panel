from flask import Flask, render_template, request, redirect, url_for, send_from_directory,session
import httplib
import os
import parse_GetAllClassesName
import parse_GetClassesJSON_bySelection
import parse_GetPointerClass
import json
from werkzeug.utils import secure_filename
 

#Initialize the app
app_parse = Flask(__name__, static_url_path = "/app_parse/",static_folder = "static/",template_folder="static/")


APPLICATION_ID = "4R03PRP8btiY00gdKqkl7lIlJyj6HYN7QFeodrfR"
MASTER_KEY = "6NtABNvHhiAz9xRUQCXMeElqhqgJQp1wItcQB9AC" #Master Key
UPLOAD_FOLDER = '/home/ubuntu/wes_old_project/res/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
#####################################################################################
#Input JSON
@app_parse.route('/app_parse/inputer', methods=['GET', 'POST'])
def DataInputer():
	MyClassesList = parse_GetAllClassesName.AllClassList()
	if request.method == 'GET':
		
		return render_template('app_parse_inputer.html', classList=MyClassesList)
	elif request.method == 'POST':
		MySelectedItems=request.form.getlist('selected_class')
		if len(MySelectedItems)!=1 or MySelectedItems[0] not in MyClassesList:
			print "\n\n***********Attack Report**********\n"+str(request.headers)
			return "You are doing something malicious!!!<br> This will be reported to admin<br>"+str(request.headers)
		return redirect(url_for('DataInputer_SpecificClass', classname=MySelectedItems[0]))
@app_parse.route('/app_parse/inputer/<classname>', methods=['GET','POST'])
def DataInputer_SpecificClass(classname):
	ExcludeTerms = ['ACL', 'createdAt', 'objectId', 'updatedAt']
	Selected_Classname = ""
	Selected_Fieldlist = []
	Selected_Typelist = []
	Selected_TargetClasslist = []
	#DateTimeSetting
	import dateutil.parser as parser
	import datetime
	str_today = str(datetime.datetime.now())
	PointerClassFieldList = parse_GetPointerClass.ClassNFieldList_SpecificPointerClass("Company")
	pter_indx = 0
	#ReturnStr=""
	MyClassesFieldList = parse_GetAllClassesName.ClassNFieldList_SpecificClass()
	for each_selected_ClassesField in MyClassesFieldList:
		if each_selected_ClassesField["className"] == classname:
			TempToBeRemoveKey = []
			for indx,each_ToBeCheckField in enumerate(each_selected_ClassesField["fields"]):
				if each_ToBeCheckField in ExcludeTerms:
					TempToBeRemoveKey.append(indx)
			for each_TempToBeRemoveKey in reversed(TempToBeRemoveKey):
				del each_selected_ClassesField["fields"][each_TempToBeRemoveKey]
				del each_selected_ClassesField["type"][each_TempToBeRemoveKey]			
			Selected_Fieldlist = each_selected_ClassesField["fields"]
			Selected_Classname = each_selected_ClassesField["className"]
			Selected_Typelist = each_selected_ClassesField["type"]
			Selected_TargetClasslist = each_selected_ClassesField["targetClass"]
			import json
			json_string=json.dumps(PointerClassFieldList)
			Selected_TargetClass = json.loads(json_string)
#retrieve pointer class and put it to app_parse_inputer_SpecificClass for selection
			
			Selected_Listlength=0			
			Selected_Date={
				"AllMonths":enumerate(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]),
				"TempMonth":1,
				"AllHours":["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24"],				
				"CountingYears":5,
				"NowYear":int(parser.parse(str_today).year),
				"NowMonth":int(parser.parse(str_today).month),
				"NowDay":int(parser.parse(str_today).day)
				}
			if len(Selected_Fieldlist) == len(Selected_Typelist):
				Selected_Listlength = len(Selected_Fieldlist)
			if request.method == 'GET':	
				return render_template('app_parse_inputer_SpecificClass.html', classname=Selected_Classname,fieldList=Selected_Fieldlist,typeList=Selected_Typelist,listLength= Selected_Listlength,date_Dict=Selected_Date,pointerClass_Dict=Selected_TargetClass)
			elif request.method == 'POST':
				import requests
				import json
				post_payload = {}
				post_headers = {"X-Parse-Application-Id":APPLICATION_ID,"X-Parse-Master-Key":MASTER_KEY,"Content-Type": "application/json"}
				
				for indx in range(Selected_Listlength):
					if Selected_Typelist[indx] == "String":
						post_payload[Selected_Fieldlist[indx]]=request.form.get('form_'+Selected_Fieldlist[indx])
					elif Selected_Typelist[indx] == "Number":
						post_payload[Selected_Fieldlist[indx]]=num(request.form.get('form_'+Selected_Fieldlist[indx]))
					elif Selected_Typelist[indx] == "Boolean":
						if request.form.get('form_'+Selected_Fieldlist[indx]) == "true":
							post_payload[Selected_Fieldlist[indx]]=True
						elif request.form.get('form_'+Selected_Fieldlist[indx]) == "false":
							post_payload[Selected_Fieldlist[indx]]=False
					elif Selected_Typelist[indx] == "Pointer":
						print 'print POINTER '
						#post_payload[Selected_Fieldlist[indx]]=request.form.get('form_'+Selected_Fieldlist[indx])
						post_payload[Selected_Fieldlist[indx]]={"__type": "Pointer","className": "Company","objectId": str(request.form.get('form_'+Selected_Fieldlist[indx]))}
						pter_indx+=1
						print str(request.form.get('form_'+Selected_Fieldlist[indx]))	
						#{"__type": "Pointer","className": "GameScore","objectId": "Ed1nuqPvc"}
						
					elif Selected_Typelist[indx] == "Date":
						TempYear=int(request.form.get('form_year_'+Selected_Fieldlist[indx]))
						TempMonth=int(request.form.get('form_month_'+Selected_Fieldlist[indx]))
						TempDate=int(request.form.get('form_day_'+Selected_Fieldlist[indx]))
						TempHour=int(request.form.get('form_hour_'+Selected_Fieldlist[indx]))
						post_payload[Selected_Fieldlist[indx]]={"__type":"Date","iso":str(datetime.datetime(TempYear, TempMonth, TempDate, TempHour, 0, 0, 0).isoformat())}
						#{"__type":"Date","iso":"2016-01-10T00:00:00.000Z"}}
					elif Selected_Typelist[indx] == "File":
						print 'TEST1'
						file = request.files['form_'+Selected_Fieldlist[indx]]
						if file :
							filename = secure_filename(file.filename)
							file.save(os.path.join(UPLOAD_FOLDER, filename))
							print 'TEST 2'+filename			
						file.seek(0)
						post_headers_file = {"X-Parse-Application-Id":APPLICATION_ID,"X-Parse-Master-Key":MASTER_KEY}		
						#sendFile = {"file": (file.filename, file.stream, file.mimetype)}		
						#sendFile = {"file": ("ibra.jpeg", open('/home/ubuntu/wes_old_project/res/Ibra001.jpeg', 'rb'),'image/jpeg', {'Expires': '0'})}		
						response = requests.post('http://127.0.0.1/parse/files/'+filename, data=open('/home/ubuntu/wes_old_project/res/'+filename, 'rb'), headers=post_headers_file)
 						print 'TEST3 + '+ response.content
						#iter(response.content).next()['_type'] = "url"
						data = json.loads(response.content)
						print 'TEST4 + '+ data["url"]
						post_payload[Selected_Fieldlist[indx]]={"name": data["name"],"url:":data["url"],"__type": "File"}
						#connection = httplib.HTTPSConnection('api.parse.com', 443)
						#connection.connect()
						#connection.request('POST','http://127.0.0.1/parse/files/pic.jpg',open('/home/ubuntu/wes_old_project/res/Ibra001.jpeg', 'rb').read(), {
						#					"X-Parse-Application-Id": APPLICATION_ID,"X-Parse-REST-API-Key": MASTER_KEY,"Content-Type": "image/jpeg"})
						#esult = json.loads(connection.getresponse().read())
						#print result
					else:
						post_payload[Selected_Fieldlist[indx]]=request.form.get('form_'+Selected_Fieldlist[indx])
					#ReturnStr+=eachField+request.form.get('form_'+eachField)+"<br>"
				response = requests.post('http://127.0.0.1/parse/classes/'+Selected_Classname, data=json.dumps(post_payload) , headers=post_headers)
				#return str(response.status_code)+ReturnStr
				return str(post_payload)+"<br>"+response.content+"<br>"+str(json.dumps(post_payload))
				return redirect(url_for('DataInputer_SpecificClass', classname=Selected_Classname))
	print "\n\n***********Attack Report**********\n"+str(request.headers)
	return "You are doing something malicious!!!<br> This will be reported to admin<br>"+str(request.headers)		
	#elif request.method == 'POST':
	#	MyClassesFieldList = parse_GetAllClassesName.ClassNFieldList_SpecificClass()
	#	ReturnStr=""
	#	for each_selected_ClassesField in MyClassesFieldList:
	#		ReturnStr+= each_selected_ClassesField["className"]+str(each_selected_ClassesField["fields"])+"<br>"
	#	return ReturnStr+"<br>Inputer"+str(len(MyClassesFieldList))+"<br>"+str(MyClassesFieldList)+str(request.headers)
	#	return send_from_directory("download/"+classname+"/",classname+".zip")#???
	#	return 0#render_template('app_parse_inputer.html', classList=MyClassesList)	#???
#####################################################################################
#Import JSON
@app_parse.route('/app_parse/importer', methods=['GET', 'POST'])
def DataImporter():
	
	return "Import"
#####################################################################################
#Outport JSON
@app_parse.route('/app_parse/exporter', methods=['GET', 'POST'])
def DataExporter():
	MyClassesList = parse_GetAllClassesName.AllClassList()
	if request.method == 'GET':
		return render_template('app_parse_exporter.html', classList=MyClassesList)
	elif request.method == 'POST':
		#First Double Check if All Data Relevant
		MySelectedItems=request.form.getlist('selected_class')
		for each_selected_class_inHTML in MySelectedItems:
			if each_selected_class_inHTML not in MyClassesList:
				print "\n\n***********Attack Report**********\n"+str(request.headers)
				return "You are doing something malicious!!!<br> This will be reported to admin<br>"+str(request.headers)
		#Prepare Download Materials:
		RandomName_ByHostNTime=parse_GetClassesJSON_bySelection.PrepareBoth_CSV_JSON(MySelectedItems)
		#Then Return Download Link
		return redirect(url_for('DataExporterFile', file=RandomName_ByHostNTime))	
	return render_template('app_parse_exporter.html', classList=MyClassesList)
	
@app_parse.route('/app_parse/exporter/<file>', methods=['GET','POST'])
def DataExporterFile(file):
	if request.method == 'GET':
		return send_from_directory("download/"+file+"/",file+".zip")
	elif request.method == 'POST':
		return render_template('app_parse_exporter.html', classList=MyClassesList)		
#####################################################################################
#Extra Function
def num(s):
	try:
		return int(s)
	except ValueError:
		return float(s)

if __name__ == '__main__':
	app_parse.run(host="0.0.0.0", port=int("10000"), debug=True)


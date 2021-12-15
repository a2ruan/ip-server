# This file serves as the View for users to interact with.

# External Libraries
from flask import Flask, jsonify, request, render_template
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
import threading
from requests import get
import time
import json
from datetime import datetime

# Internal Libraries
from ip_map import *

CLOCK_RATE_SECONDS = 1 # this indicates that the GPIO pins on the Raspberry Pi should be updated every 10ms

app = Flask(__name__)
ipmap = None

class Controller(Resource):
	def get(self, command):
		print(command)
		if command == "status-dict":
			print("status-dict")
			networkmap = ipmap.network_map
			return networkmap
		elif command == "update":
			print("Rescanning subnets and ip addresses")
			ipmap.update_map()
			return {"Status":"Rescanning subnets and ip addresses"}
		elif command.find('addsubnet=') == 0:
			command = command[10:]
			command = command + "/24"
			print("Adding subnet " + command)
			ipmap.add_subnet(command)
			return {"Status":"Adding subnet " + command}
		elif command.find('deletesubnet=') == 0:
			command = command[13:]
			print("Removing subnet " + command)
			ipmap.remove_subnet(command)
			return {"Status":"Delete subnet " + command}
		elif command.find('addip=') == 0:
			command = command[6:]
			print("Adding ip " + command)
			ipmap.add_ip(command)
			return {"Status":"Adding ip " + command}
		elif command.find('deleteip=') == 0:
			command = command[9:]
			print("Removing ip " + command)
			ipmap.delete_ip(command)
			return {"Status":"Removing ip " + command}
		elif command == "scanlist":
			scanlist = ipmap.get_scanlist_as_dict()
			return scanlist
		return {"Status":"Invalid Entry"}

class ControllerNode(Resource):
	@app.route('/')
	def get(self, relay_name, command):
		print(command)
		print(relay_name)

		if command == "status":
			print("User requested IP address")
			time.sleep(CLOCK_RATE_SECONDS*10)
			return {"Status":"status"}
		elif command.find('jenkins=') == 0:
			command = command[8:]
			print("Changing Jenkins mode to: " + command)
			if command.lower().find('off') == 0:
				print("off")
				ipmap.set_jenkins_enabled(relay_name,False)
			elif command.lower().find('on') == 0:
				print("on")
				ipmap.set_jenkins_enabled(relay_name,True)
			return {"Status":"jenkins"}

		return {"Status":"Invalid Entry"}
	
@app.route('/status')
def render_ip_table():
	networkmap = ipmap.network_map
	return render_template('status_template.html',data=networkmap)

def get_time(): # Returns time as a string
	now = datetime.now()
	return now.strftime("%H:%M:%S")

def get_date(): # Returns time as a string
	now = datetime.now()
	return now.strftime("%d/%m/%Y")

def init_webserver():
	'''
	Read/write/store IP networking information
	'''
	# Initialize IPMap
	global ipmap
	ipmap = IpMap()

	counter_clock = 0
	while True:
		time.sleep(CLOCK_RATE_SECONDS) # polling frequency is 10ms.  
		counter_clock += 1
		now = datetime.now()
		current_time = now.strftime("%d/%m/%Y %H:%M:%S")
		print("Current Time", current_time)
		#print(ipmap.ip_scan_list)

if __name__ == "__main__":
	
	# Initialize seperate thread to read/write/store IP networking information
	server = threading.Thread(target=init_webserver)
	server.start()

	# Initialize Flask webserver to recieve REST API calls
	api = Api(app)
	api.add_resource(Controller,'/<string:command>') # REST calls for entire board
	api.add_resource(ControllerNode,'/<string:relay_name>/<string:command>') # REST calls for specific pins
	print("Starting REST API server")
	app.run(host='0.0.0.0', port = 5000,debug=True, threaded=True, use_reloader=False) # 0.0.0.0 means localhost on machine that the script is running on.
#!/usr/bin/python3
import http.server
import threading
from socketserver import ThreadingMixIn
import argparse
from urllib.parse import urlparse
from urllib.parse import parse_qs
import os
import sys
import generators.editoffice
import generators.editaccess
import generators.edithta
import generators.editgadget2jscript



'''
Defining global variables. Change them if you want.
'''
#Globals
logfilename = "server-log.txt"
payload_output_dirname = "payload-output"
initialDirectory = os.getcwd()
serverPort = 80

#Word Payload Config
word_payload_name = "word-macro-test.docm"
word_template_path = "./templates/wordMacro/word-macro-test"

#Excel Payload Config
excel_payload_name = "excel-macro-test.xlsm"
excel_template_path = "./templates/excelMacro/excel-macro-test"


#HTA Payload Config
hta_payload_name = "hta-template.hta"
hta_payload_location = "./templates/HTMLApplication/"
#HTA Gadget to JScript Config
compiled_gadget_location = "./templates/HTMLApplication/decoded-gadget.exe"
hta_gadget_payload_name = "gadget-jscript-template.hta"

#Same tempalte location as HTAs
#decode_and_replace_gadget(gadget_template_location, url, output_file, compiled_gadget_location):
#

#Access Payload Config
accdb_payload_name = "access-macro-test.accde"
accdb_payload_location = "./templates/accessMacro/"




parser=argparse.ArgumentParser()
parser.add_argument('--host',help='The IP address or domain name for payload tests to report back to. All connections are made via HTTP on port 80.',required=True)
parser.add_argument('--serve-files',help='Enable to serve the test payload files using this server. True/False',dest='servefiles', action='store_true')
parser.add_argument('--generate-payloads',help='Generate the payload files', dest='generatePayloads', action='store_true')
parser.add_argument('--run-server', help='Enables the reporting server to listen for payload callbacks', dest='runServer', action='store_true')
parser.add_argument('--listen-port',help='The port that the server will listen on. If not set, default is 80',
	type=int,default=80,required=False)
parser.add_argument('--connect-port',help='The port that the payloads will connect back to. If not set, default is the same value as --listen-port',
	type=int,required=False)
args=parser.parse_args()


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
	def do_GET(self):

		if '/report.html' in self.path:
			query_components = parse_qs(urlparse(self.path).query)

			if 'msg' in query_components:
				message = query_components["msg"][0]
				log_file=open(os.path.join(initialDirectory, logfilename), "a+")
				logmsg = "From: [" + self.client_address[0] + "]: " + "Received message: " + message 
				log_file.write(logmsg)
				print(f"{bcolors.OKGREEN}" + logmsg + f"{bcolors.ENDC}")


			exit = """
				<html>
				<body>
					Message received, closing this window..
					<script>
						self.close();
					</script>
				</body>
				</html>
				"""
			#For some reason, if we leave proper response headers in, the server passes requests through to SimpleHTTPRequestHandler
			#This causes annoying duplicate logging. So, malformed response (which browswers handle on their end) it is!
			#self.send_response(200)
			#self.send_header("Content-Type", "text/html")
			#self.end_headers()
			self.wfile.write(bytes(exit, "utf8"))
			

		elif self.path == "/" or not args.servefiles:
			self.send_response(401)

		elif self.path == "/requestfiles.html":
			self.path = "/"
			return http.server.SimpleHTTPRequestHandler.do_GET(self)	    

		else:
			return http.server.SimpleHTTPRequestHandler.do_GET(self)

class ThreadingHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    pass

if __name__ == "__main__":

	if args.connect_port:
		reportURL = "http://" + args.host + ":" + str(args.connect_port)
	else: 
		reportURL = "http://" + args.host + ":" + str(args.listen_port)

	if args.generatePayloads:
		#Create our word document
		print(f"{bcolors.HEADER}Generating test payloads which report back to " + reportURL + f"{bcolors.ENDC}")
		print("-"*70)

		try:
			generators.editoffice.edit_Macro_Properties(reportURL, os.path.join(initialDirectory, payload_output_dirname),
				word_template_path, word_payload_name)
		except Exception as e:
			print(f"{bcolors.FAIL}Failed to create the Word macro test file: {bcolors.ENDC}")
			print(e)

		try:
			generators.editoffice.edit_Macro_Properties(reportURL, os.path.join(initialDirectory, payload_output_dirname), excel_template_path, excel_payload_name)
		except Exception as e:
			print(f"{bcolors.FAIL}Failed to create the Excel macro test file: {bcolors.ENDC}")
			print(e)

		try:
			generators.editaccess.open_and_write_accessdb(os.path.join(accdb_payload_location, accdb_payload_name), 
			reportURL, os.path.join(payload_output_dirname, accdb_payload_name))
		except Exception as e:
			print(f"{bcolors.FAIL}Failed to create the Access macro test file: {bcolors.ENDC}")
			print(e)

		try:
			generators.edithta.open_and_write_hta(os.path.join(hta_payload_location, hta_payload_name), 
			reportURL, os.path.join(payload_output_dirname, "hta-test.hta"))
		except Exception as e:
			print(f"{bcolors.FAIL}Failed to create the HTA test file: {bcolors.ENDC}")
			print(e)
		try:
			generators.editgadget2jscript.decode_and_replace_gadget(os.path.join(hta_payload_location, hta_gadget_payload_name), 
			reportURL, os.path.join(payload_output_dirname, hta_gadget_payload_name), compiled_gadget_location)
		except Exception as e:
			print(f"{bcolors.FAIL}Failed to create the HTA GadgetToJScript test file: {bcolors.ENDC}")
			print(e)
		print("\n"*3)


	if args.runServer:
		#Change into the payload-output directory to only serve necessary files
		os.chdir(os.path.join(initialDirectory, "payload-output"))
		print(f"{bcolors.HEADER}Server listening for payload callbacks at 0.0.0.0:" + str(args.listen_port) + f"{bcolors.ENDC}")

		if args.servefiles:
			print("Payloads can be downloaded from " + reportURL + "/requestfiles.html")
		print("-"*70)
		try:
			handler_object = MyHttpRequestHandler
			my_server = ThreadingHTTPServer(("0.0.0.0", args.listen_port), handler_object)
			# Start the server
			my_server.serve_forever()
		except Exception as e:
			my_server.shutdown()
			#print(f"{bcolors.FAIL}ERROR: Failed to start the web server, exception: {bcolors.ENDC}")
			#print(e)


	if not args.runServer and not args.generatePayloads:
		print(f"{bcolors.FAIL}Enable --run-server, --generate-payloads, or both to use this script.{bcolors.ENDC}")

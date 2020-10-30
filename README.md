# SurfaceToCloud
Generates, hosts, and tracks reporting of common payload delivery types (i.e. macro documents, HTA, etc). Helpful for determining the available executable surface on client workstations in a white-box assessment.

# Purpose
SurfaceToCloud is useful in white-box testing scenarios involving payload delivery during a penetration test (typically Electronic Social Engineering [ESE] engagements). The idea behind this utility is to determine if any payload delivery techniques are available for the tester on a client's workstation. Clients deploy a wide range of solutions and workstation hardening configurations to prevent initial payload execution, and there is nothing more aggrivating then devoting time to crafting an _actual_ payload (one containing C2 comms), to find out that your method of staging (i.e. a macro using WScript.Shell) is blocked out of the box by their Next-Gen AntiVirus or workstation hardening policies. 

SurfaceToCloud will generate multiple files which are commonly used for staging payloads and host them on your web server. Working with your client, they can be directed to download and run each file listed on the web page. The files, on opening, will send an HTTP request back to SurfaceToCloud indicating if they were successful in running, which lets you know that it is a possible route to take for staging your real payload.

# How to Use
```
usage: SurfaceToCloud.py [-h] --host HOST [--serve-files]
                         [--generate-payloads] [--run-server]
                         [--listen-port LISTEN_PORT]
                         [--connect-port CONNECT_PORT]

optional arguments:
  -h, --help                  show this help message and exit
  --host HOST                 The IP address or domain name for payload tests to report back to. All connections are made via HTTP on port 80.
  --serve-files               Enable to serve the test payload files using this server. True/False
  --generate-payloads         Generate the payload files
  --run-server                Enables the reporting server to listen for payload callbacks
  --listen-port LISTEN_PORT   The port that the server will listen on. If not set, default is 80
  --connect-port CONNECT_PORT The port that the payloads will connect back to. If not set, default is the same value as --listen-port. This is useful for when using redirectors which listen on a standard port and point to a non-standard.
```

**Example: Generate all payloads, calling back to 192.168.1.10, and host them on the web server**
```SurfaceToCloud.py --host 192.168.1.10 --generate-payloads --run-server --serve-files```

**Example: Only generate payloads that call back to 192.168.1.10 and then quit**
```SurfaceToCloud.py --host 192.168.1.10 --generate-payloads```

**Example: Serve files from the ./payload-output directory and listen for resposnes, but do not re-generate payloads**
```SurfaceToCloud.py --host 192.168.1.10 --run-server --serve-files```


# Payload Reporting / Callbacks
Payloads call back to the server using HTTP, sending a message indicating that they ran. The table below indicates all available staging file types, their included call-back messages (some files have multiple call-backs, testing for things like WScript.Shell usage ontop of general Macro execution), and what the messages mean. If you see a message returned to the server, it means that portion of the payload has successfully executed.

Payload File Name | Description | Callback Messages
----------------- | ----------- | -----------------
word-macro-test.docm | Microsoft Word Macro, tests for the ability to run macros, and then checks if WScript.Shell can execute cmd.exe (runs internet explorer to test and send the message). | Messsage: Word Doc Macro Executed <br> Meaning: The macro has successfully executed, allowing for an XMLHTTP Request to be made. <br><br> Message: Success Word Doc WScript Execution IExplorer <br> Meaning: The macro was able to successfully run WScript.Shell with a .Run("cmd.exe /k start iexplore.exe"). Many payloads use WScript.Shell with .Run, which can be blocked by default by some NG-AV (i.e. Cylance script-block). 
excel-macro-test.xlsm | Microsoft Excel Macro, tests for the ability to run macros, and then checks if WScript.Shell can execute cmd.exe (runs internet explorer to test and send the message). | Messsage: Excel Doc Macro Executed <br> Meaning: The macro has successfully executed, allowing for an XMLHTTP Request to be made. <br><br> Message: Success Excel Doc WScript Execution IExplorer <br> Meaning: The macro was able to successfully run WScript.Shell with a .Run("cmd.exe /k start iexplore.exe"). Many payloads use WScript.Shell with .Run, which can be blocked by default by some NG-AV (i.e. Cylance script-block). 
hta-test.hta | HTML Application, tests using Shell.Application and WScript.Shell to execute/open Internet Explorer (XMLHTTP requests from a document downloaded from the internet with Mark of the Web (MoTW) are prevented by default on Windows in an HTA. | Message: HTA Shell.Application Executed Internet Explorer <br> Meaning: The message spells it out. Internet Explorer was able to be run using Shell.Application within the HTA. <br><br>Message: WScript.Shell Executed in Internet Explorer<br>Meaning: The HTA successfully ran  WScript.Shell with .Run("cmd.exe /k start iexplore.exe") to start Internet Explorer
gadget-jscript-template.hta | HTML Application, Executes serialized C# as a Gadget (uses GadgetToJScript) | Message: Successfully Executed CSharp from Gadget<br>Meaning: Success message! GadgetToJScript is viable. It ran the C# code which made an HTTP request using WebClient. 
access-macro-test.accde | Microsoft Access Macro as an Executable Only File (accde), tests running Macrcos in Microsoft Access. ACCDEs have less prompts than normal access documents with macros (.accdb) | Message: Access Macro Executed<br>Meaning: The macro has successfully executed, allowing for an XMLHTTP Request to be made. <br><br> Message: Success Access Macro WScript Execution IExplorer <br> Meaning: The macro was able to successfully run WScript.Shell with a .Run("cmd.exe /k start iexplore.exe"). Many payloads use WScript.Shell with .Run, which can be blocked by default by some NG-AV (i.e. Cylance script-block). 


# Random Nuances / Notes:
* The host URL+port cannot result in a string longer than 122 characters. Some trickery was done to modify binary files, with character replacement and padding, because I didn't think people would want to have to run this on Windows or install dotnet core. This will break the ACCDE and GadgetToJScript Payloads
* For Excel and Word, custom properties are added to allow URLs to be modified/replaced in custom.xml. Much simpler. The custom property created/used is "setURL".
* Internet Explorer is opened a lot on your client's workstation (twice per payload typically). The page it opens will try to auto-close itself. However, a pop-up will ask if they want to let the window close itself. Have them just click "yes".


# Features to Add
* Not sure if it is worth it, or to do this once a payload stager method has been selected, but determine possibile usage of common LoLBINs?
* More pop-ups.. but maybe add Shell.Application checks to all Macro payloads and not just HTAs, since some NG-AV engines block WScript.Shell's .Run but not Shell.Application.

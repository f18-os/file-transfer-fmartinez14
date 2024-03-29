#! /usr/bin/env python3

# Echo client program
import sys
sys.path.append("../lib")       # for params

import re,params,socket

from framedSock import framedSend, framedReceive


switchesVarDefaults = ( #Default parameters
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-f', '--fileName') , 'file_name', "fileFromClient.txt"),
    (('-p', '--protocol') , 'protocol', "PUT"),
    (('-d', '--debug'), "debug", True), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, file_name, protocol, usage, debug  = paramMap["server"], paramMap["file_name"], paramMap["protocol"], paramMap["usage"], paramMap["debug"]
#Default variables and parameters.
currBuf = ""
bufferIsComplete = False
if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)

except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('could not open socket')
    sys.exit(1)


print(protocol + " " + file_name) #Prints and send commands.
sendParameters = protocol + " " + file_name
framedSend(s, str.encode(sendParameters), debug)
allSet = framedReceive(s, debug)

try:
    if protocol == "PUT":
        with open("filesFolder/client/" + file_name, 'r') as outputFile:
            currBuf += outputFile.read()
        outputFile.close() #Writes to buffer and closes file. Adding delimeter at end.
        currBuf += " !@#___!@# "
        while currBuf:
            sendMe = currBuf[:100]
            print("sending: " + sendMe + " " + str(len(sendMe))) #Sends packets at 100 bytes at a time and then closes the socket. Move buffer by the amount of bytes recieved back.
            framedSend(s,str.encode(sendMe), debug)
            tempVar = framedReceive(s, debug)
            bytesToMove = len(tempVar.decode())
            print("got back:" + tempVar.decode())
            currBuf = currBuf[bytesToMove:]

        s.close()
        print("Sucessfully sent file.")

    elif protocol== "GET":
        while not bufferIsComplete:
            tempStr = framedReceive(s,debug)
            sendBack = tempStr
            tempStr = tempStr.decode() #Recieve the information until the buffer is complete.
            print("Recieved: " + tempStr + " " + str(len(tempStr)))
            if " !@#___!@# " in tempStr:
                writeFile, delimeter = tempStr.split(" !@#___!@# ")
                currBuf += writeFile #if delimeter is found, stop.
                bufferIsComplete = True
            if len(tempStr) < 100: #Or if buffer is less than a 100.
                bufferIsComplete = True
            else:
                currBuf += tempStr

            framedSend(s,sendBack,debug)

        if currBuf and protocol == "GET":
            print(file_name + " writing:" + currBuf)
            with open("filesFolder/client/" + file_name, 'a+') as outputFile:
                outputFile.write(currBuf)
            currBuf = "" #Write to file once sending from server is complete.
            outputFile.close()
except:
    print("There has been an error, please try again with an existing file.")

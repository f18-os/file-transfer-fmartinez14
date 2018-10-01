#! /usr/bin/env python3

# Echo client program
import sys
sys.path.append("../lib")       # for params

import re,params,socket

from framedSock import framedSend, framedReceive


switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-f', '--fileName') , 'file_name', "fileFromClient.txt"),
    (('-p', '--protocol') , 'protocol', "PUT"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, file_name, protocol, usage, debug  = paramMap["server"], paramMap["file_name"], paramMap["protocol"], paramMap["usage"], paramMap["debug"]

currBuf = ""
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


print(protocol + " " + file_name)
sendParameters = protocol + " " + file_name
framedSend(s, str.encode(sendParameters), debug)
allSet = framedReceive(s, debug)


if protocol == "PUT":
    with open("filesFolder/client/" + file_name, 'r') as outputFile:
        currBuf += outputFile.read()
    outputFile.close()
    currBuf += " !@#___!@#      |||&&&***"
    while currBuf:
        print("sending: " + currBuf + " " + str(len(currBuf)))
        framedSend(s,str.encode(currBuf), debug)
        tempVar = framedReceive(s, debug)
        bytesToMove = len(tempVar.decode())
        print("got back:" + tempVar.decode())
        currBuf = currBuf[bytesToMove:]
    s.close()
print("Sucessfully sent file.")



# print("sending hello world")
# framedSend(s, b"hello world", debug)
# print("received:", framedReceive(s, debug))

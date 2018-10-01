#! /usr/bin/env python3


import sys
sys.path.append("../lib")       # for params
import os, socket, params


switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']


if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

while True:
    print("Connection Starting")
    sock, addr = lsock.accept()
    file_name= ""
    protocol= ""
    from framedSock import framedSend, framedReceive

    if not os.fork():
        print("new child process handling connection from", addr)
        currBuf = ""
        bufferIsComplete = False
        while True:
            payload = framedReceive(sock, debug)
            if debug: print("rec'd: ", payload)
            if not payload:
                if debug: print("child exiting")
                sys.exit(0)
            print(payload)

            # payload += b"!"             # make emphatic!

            if not file_name:
                tempVar = payload.decode()
                protocol, file_name = tempVar.split(" ")
                print(protocol + " " + file_name)
                framedSend(sock,payload, debug)

            if protocol == "PUT":
                while not bufferIsComplete:
                    tempStr = framedReceive(sock,debug)
                    sendBack = tempStr
                    tempStr = tempStr.decode()
                    print("Recieved: " + tempStr + " " + str(len(tempStr)))
                    if " !@#___!@# " in tempStr:
                        writeFile, delimeter = tempStr.split(" !@#___!@# ")
                        currBuf += writeFile
                        bufferIsComplete = True
                    else:
                        currBuf += tempStr

                    framedSend(sock,sendBack,debug)

                if currBuf and protocol == "PUT":
                    print(file_name + " writing:" + currBuf)
                    with open("filesFolder/server/" + file_name, 'a+') as outputFile:
                        outputFile.write(currBuf)
                    currBuf = ""
                    outputFile.close()

            elif protocol== "GET":
                with open("filesFolder/server/" + file_name, 'r') as outputFile:
                    currBuf += outputFile.read()
                outputFile.close()
                currBuf += " !@#___!@#      |||&&&***"
                while currBuf:
                    print("sending: " + currBuf + " " + str(len(currBuf)))
                    framedSend(sock,str.encode(currBuf), debug)
                    tempVar = framedReceive(sock, debug)
                    bytesToMove = len(tempVar.decode())
                    print("got back:" + tempVar.decode())
                    currBuf = currBuf[bytesToMove:]
                print("Sucessfully sent file.")


            print("Connection Terminated")

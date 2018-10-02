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

            if not file_name: #If file name is empty, that means we are recieving parameters.
                tempVar = payload.decode()
                protocol, file_name = tempVar.split(" ")
                print(protocol + " " + file_name)
                framedSend(sock,payload, debug)

            if protocol == "PUT":
                while not bufferIsComplete:
                    tempStr = framedReceive(sock,debug)
                    sendBack = tempStr #Same logic as client , recieve the information until the delimeter or the buffer is less than 100.
                    tempStr = tempStr.decode()
                    print("Recieved: " + tempStr + " " + str(len(tempStr)))
                    if " !@#___!@# " in tempStr:
                        writeFile, delimeter = tempStr.split(" !@#___!@# ")
                        currBuf += writeFile
                        bufferIsComplete = True
                    if len(tempStr) < 100:
                        bufferIsComplete = True
                    else:
                        currBuf += tempStr
                        tempStr = ""

                    framedSend(sock,sendBack,debug)

                if currBuf and protocol == "PUT": #Write to file once buffer is complete.
                    print(file_name + " writing:" + currBuf)
                    with open("filesFolder/server/" + file_name, 'a+') as outputFile:
                        outputFile.write(currBuf)
                    currBuf = ""
                    outputFile.close()

            elif protocol== "GET": #Read file same as client and send 100 bytes at a time.
                with open("filesFolder/server/" + file_name, 'r') as outputFile:
                    currBuf += outputFile.read().strip()
                outputFile.close()
                currBuf += " !@#___!@# "
                while currBuf:
                    sendMe = currBuf[:100]
                    print("sending: " + sendMe + " " + str(len(sendMe)))
                    framedSend(sock,str.encode(sendMe), debug)
                    tempVar = framedReceive(sock, debug)
                    bytesToMove = len(tempVar.decode())
                    print("got back:" + tempVar.decode())
                    currBuf = currBuf[bytesToMove:] #Move buffer  by the amount of bytes recieved.
                print("Sucessfully sent file.")


            print("Connection Terminated")

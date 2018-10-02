This project allows you to do a TCP transfer of files.


This transfer can be done with either the PUT or GET protocol.  


The usage is as follows:

For client:

#python3 framedClient.py -s 127.0.0.1:50000 -f testFileFromServer.txt -p GET

For Server:
#python3 framedForkServer.py -l 50001


You may change these parameters to change protocol or server. It supports both PUT and GET.


Files are saved inside the /filesFolder/client and /filesFolder/server/ folders. You can transfer using those directories.

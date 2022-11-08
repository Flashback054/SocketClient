import sys
import clientsocketlib as client

PORT=80

# RUN

# MANUALLY INPUT THROUGH COMMAND LINE
if (len(sys.argv) > 1):
    if (len(sys.argv) == 2): # only 1 addr provided => single connection download
        hostaddr=sys.argv[1]
        if (hostaddr[len(hostaddr)-1]=='/'): # download all files from folder
            client.downloadAllFiles(hostaddr,PORT)
        else:
            client.downloadFile(hostaddr,PORT)
    else: # multiconnection download
        connectionList=[]
        for i in range(1,len(sys.argv)):
            connectionList.append((sys.argv[i],PORT))
        client.multiConnectionDownload(connectionList)
else:
    print('No arguments provided.')

# ----- OR UNCOMMENT TO USE TESTCASES -----
# Download : Content-Length:
# client.downloadFile('http://example.com',PORT)
# client.downloadFile('http://web.stanford.edu/class/cs231a/course_notes/01-camera-models.pdf',PORT)

# Download : Chunked
# client.downloadFile('http://www.httpwatch.com/httpgallery/chunked/chunkedimage.aspx',PORT)
# client.downloadFile('http://www.bing.com',PORT)
# client.downloadFile('http://anglesharp.azurewebsites.net/Chunked',PORT)

# Download All Files
# client.downloadAllFiles('http://web.stanford.edu/class/cs143/handouts/',PORT)
# client.downloadAllFiles('http://web.stanford.edu/class/cs231a/course_notes/',PORT)

# Multiconnection Download
# connectionList=[
#     ('http://example.com',PORT),
#     ('http://web.stanford.edu/class/cs231a/course_notes/01-camera-models.pdf',PORT),
#     ('http://www.httpwatch.com/httpgallery/chunked/chunkedimage.aspx',PORT),
#     ('http://www.bing.com',PORT),
#     ('http://web.stanford.edu/class/cs231a/course_notes/',PORT),
#     ('http://web.stanford.edu/class/cs143/handouts/',PORT),
#     ('http://www.google.com/index.html',PORT),
#     ('http://web.stanford.edu/class/cs142/lectures/',PORT)
# ]
# client.multiConnectionDownload(connectionList)



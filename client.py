import clientsocketlib as client
PORT=80

# RUN

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
connectionList=[
    ('http://example.com',PORT),
    ('http://web.stanford.edu/class/cs231a/course_notes/01-camera-models.pdf',PORT),
    ('http://www.httpwatch.com/httpgallery/chunked/chunkedimage.aspx',PORT),
    ('http://www.bing.com',PORT),
    ('http://web.stanford.edu/class/cs231a/course_notes/',PORT),
    ('http://web.stanford.edu/class/cs143/handouts/',PORT)
]
client.multiConnectionDownload(connectionList)



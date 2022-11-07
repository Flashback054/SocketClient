import socket
import threading
import os

class Header:
    def __init__(self,sock) -> None:
        try:
            self.statusLine=getLine(sock)
            
            self.statusCode=int(self.statusLine[self.statusLine.find(' ')+1 : self.statusLine.find(' ')+4])

            while True:
                line=getLine(sock)
                if (line=='\r\n'):
                    break
                else:
                    # ex: Content-Length: 100\r\n ===>headerField='Content-Length', fieldValue='100'
                    headerField=line[0:line.find(':')]
                    fieldValue=line[line.find(': ') + 2 : len(line) - 2]
                    setattr(self,headerField,fieldValue)
        except socket.error as err :
            raise err
        except Exception as exp:
            raise exp

    def isChunkedEncoding(self):
        if (hasattr(self,'Transfer-Encoding')):
            if (getattr(self,'Transfer-Encoding')=='chunked'):
                return True
        return False

    def getContentLength(self):
        if (hasattr(self,'Content-Length')):
            return int(getattr(self,'Content-Length'))
        else:
            return -1

    def getFileFormat(self):
        contentType = getattr(self,'Content-Type')
        if (contentType.find(';')!=-1): # ex: Content-Type: application/json; charset=utf-8...
            formatField=contentType[0 : contentType.find(';')]
            fileFormat=formatField[formatField.rfind('/') + 1 : ]
        else:
            fileFormat=contentType[contentType.rfind('/') + 1: ]
        return fileFormat

class Response:
    def __init__(self,sock) -> None:
        self.header=Header(sock)
        self.content=""

    def getContent(self,sock,header):
        try:
            if (header.isChunkedEncoding()):
                content=self.getContentFromChunks(sock)
            else:
                contentLength=self.header.getContentLength()
                if (contentLength!=-1):
                    content=self.getContentFromContentLength(sock,contentLength)    

            return content
        except socket.err as sockErr:
            raise sockErr
        except Exception as exp:
            raise exp

    def getContentFromContentLength(self,sock,contentLength):
        try:
            content=recv_s(sock,contentLength)
            return content
        except socket.error as err :
            raise err
        except Exception as exp:
            raise exp

    def getContentFromChunks(self,sock):
        try:
            content=[]
            while True:
                sizeLine=getLine(sock)
                # omit '\r\n'
                if (sizeLine.find(';')!=-1): #chunk extension included
                    sizeLine=sizeLine[0:sizeLine.find(';')].strip()
                else:
                    sizeLine=sizeLine[0:len(sizeLine)-2].strip()

                size=int(sizeLine,16)
                if (size==0):
                    break
                else:
                    chunk=recv_s(sock,size)
                    content.append(chunk)
                    last=getLine(sock) # discard last \r\n

            self.getAndDiscardTrailer(sock)

            return b"".join(content)
        
        except socket.error as err :
            raise err
        except Exception as exp:
            raise exp

    def getAndDiscardTrailer(self,sock):
        try :
            while True:
                line=getLine(sock)
                if (not line):
                    break
                if (line in ('','\r\n','\n','')):
                    break
        except socket.error as err :
            raise err
        except Exception as exp:
            raise exp

    def getDecodedContent(self,format):
        return self.content.decode(format)

    def getUrlsFromContent(self,content,hostAddr):
        urls=[]
        curPos=0
        while True:
            #find all <a> tags
            curPos=content.find('<a',curPos)
            if (curPos==-1):
                break
            urlPos=content.find('href=',curPos)+6
            quote=content[urlPos-1] # quote is '' or ""
            url=content[urlPos:content.find(quote,urlPos)]
            if (url not in("","#") and url[0]!='?'): # not file url
                # Url is relative, else url is absolute
                if (url.find('http')==-1):
                    if (url[0]!='/'): 
                        urls.append(hostAddr+url)
                    else:
                        urls.append(hostAddr+url[1:]) # discard '/' in front of url
                else:
                    url.append(url)
            curPos+=1
        
        return urls

def initConnection(HOST,PORT):
    try:
        hostIP=socket.gethostbyname(HOST)
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((hostIP,PORT))
        return sock
    except socket.error as err:
        raise err
    except socket.gaierror as gaierr:
        raise gaierr

def splitHostAndPath(HOST):
    # Split url into Host and Path
    hostIndex=HOST.find('//')+2
    filePathIndex=HOST.find('/',hostIndex)

    # HOST addr doesn't include path , ex:"http://example.com"
    if (filePathIndex==-1):
        host=HOST[hostIndex:]
        path=''
    else:
        host=HOST[hostIndex:filePathIndex]
        path=HOST[filePathIndex+1:]
    
    return (host,path)

def sendGETRequest(sock,host,path):
    try:
        request=f'GET /{path} HTTP/1.1\r\nHost: {host}\r\nConnection: Keep-alive\r\n\r\n'
        sock.sendall(request.encode('utf-8'))
    except socket.error as err :
        raise err

# safely receive n bytes from socket
def recv_s(sock,nbytes):
    try:
        remain=nbytes
        result=[]
        while True:
            data=sock.recv(remain)
            if (len(data)==0): # server has closed the socket
                raise Exception('Server has closed the socket.')
            
            remain-=len(data)
            result.append(data)
            if (remain==0):
                break

        return b"".join(result)
    except socket.error as err:
        raise err
    except Exception as exp:
        raise exp

# Get a line from socket
def getLine(sock):
    try:
        lines=[]

        while True:
            chr=recv_s(sock,1)         
            lines.append(chr)
            # if lines is "...\r\n"
            if (len(lines)>=2 and lines[len(lines)-2]==b'\r' and lines[len(lines)-1]==b'\n'):
                break

        result=(b"".join(lines)).decode('utf-8')
        return result
    except socket.error as err:
        raise err
    except Exception as exp:
        raise exp

# Write File
def createFileFromData(path,data):
    try:
        file=open(f'{path}','wb')
        file.write(data)
        file.close()
    except OSError as oserr:
        raise oserr

### MAIN FUNCTION ###

def downloadFile(HOST,PORT): 
    try: 
        handleDownloadFile(HOST,PORT)
    except socket.error as sockErr:
        print(f'Socket error downloading file from {HOST} : {sockErr}')
    except socket.gaierror as gaiErr:
        print(f'Get address info error during downloading file from {HOST} : {gaiErr}')
    except OSError as osErr:
        print(f'Error writing file downloaded from {HOST} : {osErr}')
    except Exception as exp:
        print(f'Exception occurred during downloading file from {HOST} : {exp}')

def downloadAllFiles(HOST,PORT):
    try:
        handleDownloadAllFiles(HOST,PORT)
    except socket.error as sockErr:
        print(f'Socket error during downloading all files from folder {HOST} : {sockErr}')
    except socket.gaierror as gaiErr:
        print(f'Get address info error during downloading all files from folder {HOST} : {gaiErr}')
    except OSError as osErr:
        print(f'Error writing files downloaded from folder {HOST} : {osErr}')
    except Exception as exp:
        print(f'Exception occurred during downloading all files from folder {HOST} : {exp}')

def handleDownloadFile(HOST,PORT):
    try:
        # split host and path from HOST addr
        # ex:http://example.com/index.html 
        # -> host:example.com, path:index.html
        (host,path)=splitHostAndPath(HOST)
        
        sock=initConnection(host,PORT)

        sendGETRequest(sock,host,path)

        # Get and parse response
        response = Response(sock)

        if (response.header.statusCode >= 200 and response.header.statusCode < 300): 
            response.content=response.getContent(sock,response.header) # return content in b"" format

            if (path==''):
                # default: index.html
                createFileFromData(f'{host}_index.html',response.content)
            else:
                fileName=path[path.rfind('/')+1:]
                createFileFromData(f'{host}_{fileName}',response.content)
        else:
            raise Exception(f'Response status code : {response.header.statusCode} .')

    except socket.error as sockErr:
        raise sockErr
    except socket.gaierror as gaiErr:
        raise gaiErr
    except OSError as oserr:
        raise oserr
    except Exception as exp:
        raise exp

    finally:
        sock.close()


def handleDownloadAllFiles(HOST,PORT):
    try:
        # split host and path from HOST addr
        # ex:http://web.stanford.edu/class/cs231a/course_notes/ 
        # -> host = web.stanford.edu, path = class/cs231a/course_notes/
        (host,path)=splitHostAndPath(HOST)
        folderName=path[path.rfind('/',0,len(path)-1)+1 : len(path)-1]

        sock=initConnection(host,PORT)

        sendGETRequest(sock,host,path)

        response = Response(sock)

        if (response.header.statusCode>=200 and response.header.statusCode<300):
            if (getattr(response.header,'Connection') == 'Keep-Alive'):
                response.content=response.getContent(sock,response.header) # return content in b"" format
                content=response.getDecodedContent('utf-8') # decode in order to parse all <a> tags

                #create folder
                currDir=os.getcwd()
                folderPath=f'{host}_{folderName}'
                os.makedirs(folderPath, exist_ok=True)

                urls=response.getUrlsFromContent(content,HOST)
                for url in urls:
                    (urlhost,urlpath)=splitHostAndPath(url)
                    fileName=urlpath[urlpath.rfind('/')+1:]
                    if (fileName!=''): # if fileName=='' ==> url refer to a folder ==> no need to download
                        sendGETRequest(sock,urlhost,urlpath)

                        subResponse = Response(sock)

                        if (subResponse.header.statusCode==200):
                            subResponse.content = subResponse.getContent(sock,subResponse.header)
                            createFileFromData(os.path.join(currDir,folderPath,fileName),subResponse.content)
            else: # Connection: Close:
                raise Exception('Server closed connection right after response')
        else: # statusCode < 200 or statusCode >= 300
            raise Exception(f'Response status code : {response.header.statusCode} .')

    except socket.error as sockErr:
        raise sockErr
    except socket.gaierror as gaiErr:
        raise gaiErr
    except OSError as osErr:
        raise osErr
    except Exception as exp:
        raise exp

    finally:
        sock.close()



def multiConnectionDownload(connectionList):
    threads=[]
    try:
        for conn in connectionList:
            (host,port)=conn
            if (host[len(host)-1]=='/'): #download all files from folder
                thread=threading.Thread(target=downloadAllFiles,args=(host,port))
            else: #download a single file
                thread=threading.Thread(target=downloadFile,args=(host,port))

            thread.start()
            threads.append(thread)
    except:
        print('Error occurred during threading.')
    finally:
        for thread in threads:
            thread.join()

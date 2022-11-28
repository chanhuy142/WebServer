import socket
import threading
import json
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

hostname=socket.gethostname()   
IPAddr=socket.gethostbyname(hostname)
server.bind(('localhost',80))
server.listen(5)
f=open('login.json','r')
data=json.load(f)
f.close()
id=data['account'][0]['id']
psw=data['account'][0]['psw']

class requestparse:
    def __init__(self, request):
        if request == "":
            self.empty = True	#if there is no request content
        else:
            requestArray = request.split("\r\n")
            self.request = request
            self.method = requestArray[0].split(" ")[0]
            self.path = requestArray[0].split(" ")[1]
            self.empty = False

def senddata(client, msg):
    request=requestparse(msg)
    print(request.method)
    print(request.path)
    filename=request.path[1:]
    

    if filename=="":
        filename="index.html"
    filetype=filename.split(".")[1]
    
    if filetype == 'html':
        filetype = 'text/html'
    elif filetype == 'css':
        filetype = 'text/css'
    elif filetype == 'png':
        filetype = 'image/png'
    try:
        file=open(filename,"rb")
        filedata=file.read()
        file.close()
    except:
        
        file=open("404.html","rb")
        filedata=file.read()
        filetype="text/html"

    if request.method == "GET":
        f = open('block.txt',"r")
        check = f.read();
        f.close()
        if check == "False":
            if (filename in ["images.html"]):
                filename  = "401.html"

        print("Sending file: "+filename)
        if filename in ["index.html"]:
            contentlenght=len(filedata)
            message_header = 'HTTP/1.1 200\r\n'
            message_header += 'Content-type: text/html\r\n'
            message_header+="Content-Length: %d\r\n"%contentlenght
            message_header += '\r\n'
            message_header = message_header.encode()
            client.sendall(message_header+filedata)
        elif filename in ["404.html"]:
            contentlenght=len(filedata)
            message_header = 'HTTP/1.1 404\r\n'
            message_header += 'Content-type: text/html\r\n'
            message_header+="Content-Length: %d\r\n"%contentlenght
            message_header += '\r\n'
            message_header = message_header.encode()
            client.sendall(message_header+filedata)
        elif filename in ["401.html"]:
            file=open("401.html","rb")
            filedata=file.read()
            contentlenght=len(filedata)
            message_header = 'HTTP/1.1 401\r\n'
            message_header += 'Content-type: text/html\r\n'
            message_header+="Content-Length: %d\r\n"%contentlenght
            message_header += '\r\n'
            message_header = message_header.encode()
            client.sendall(message_header+filedata)
        else:
            contentlenght=len(filedata)
            message_header = 'HTTP/1.1 200\r\n'
            message_header += 'Content-type: %s\r\n'%filetype
            message_header+="Content-Length: %d\r\n"%contentlenght
            message_header += '\r\n'
            message_header = message_header.encode()
            client.sendall(message_header+filedata)
        f = open('block.txt',"w")
        f.write("False")
        f.close()

    elif request.method == "POST":
        logininfo=request.request.split("\r\n\r\n")[-1]
        print("logininfo:  ",logininfo)
        username=logininfo.split("&")[0].split("=")[-1]
        password=logininfo.split("&")[1].split("=")[-1]
        print("username:  ",username)
        print("password:  ",password)
        if username==id and password==psw:
            header='HTTP/1.1 303 See Other\r\nLocation: /images.html\r\n\r\n'
            client.sendall(header.encode())
            f = open('block.txt',"w")
            f.write("True")
        else:
            file=open("401.html","rb")
            filedata=file.read()
            filetype="text/html"
            contentlenght=len(filedata)
            message_header = 'HTTP/1.1 401\r\n'
            message_header += 'Content-type: text/html\r\n'
            message_header+="Content-Length: %d\r\n"%contentlenght
            message_header += '\r\n'
            message_header = message_header.encode()
            client.sendall(message_header+filedata)

        
        
        


def handle(connect):
    msg = connect.recv(1024)
        
    print("--------------------")
    while msg:
        #print(msg.decode())
        senddata(connect, msg.decode())
        print("--------------------")
        msg = connect.recv(1024)
    print("Connection closed")
    connect.close()

    return 0

        

def startserver():
    print("Server started")
    
    while True:
        try:
            connect, addr = server.accept()
            print(addr, "connected")
            threading.Thread(target=handle, args=(connect,)).start()
        except:
            print("error")
            server.close()
            break
    return 0

if __name__ == "__main__":
    startserver()
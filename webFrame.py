#coding:UTF-8

"""
一个基于python的web框架
该框架仅仅使用一个py文件，目标为轻量级框架
@author:yubang
时间：2015-02-25
"""


from SocketServer import ThreadingTCPServer, StreamRequestHandler
from cgi import parse_qs
from wsgiref.simple_server import make_server
import traceback,time,json,hashlib,re,urllib

handleMethod=None
sessionKey="sessionId"
cache=None
debug=True

class Cache():
    "缓存类"
    def __init__(self,type):
        global debug
        self.__debug=debug
        self.__data={}
        self.__timeout={}
        self.__type=type
        self.__count=0
    def __log(self,data):
        "输出日记"
        if(self.__debug):
            print data
            print unicode("当前计数："+str(self.__count),"UTF-8")
    def set(self,key,value,timeout=3600):
        "设置"
        key=hashlib.md5(key).hexdigest()
        if(self.__type=="simple"):
            if(self.__count>=5000):
                self.__deleteTimeoutData()
            if(not self.__data.has_key(key)):
                self.__count=self.__count+1
            self.__data[key]=value
            self.__timeout[key]=time.time()+timeout
            self.__log(unicode("设置key:"+key+":"+value,"UTF-8"))
    def get(self,key):
        "获取"
        key=hashlib.md5(key).hexdigest()
        if(self.__type=="simple"):
            if(self.__data.has_key(key)):
                if(time.time()<self.__timeout[key]):
                    self.__log(unicode("命中key:"+key,"UTF-8"))
                    return self.__data[key]
                else:
                    self.__log(unicode("过期key:"+key,"UTF-8"))
                    self.delete(key)
                    return None
            else:
                self.__log(unicode("丢失key:"+key,"UTF-8"))
                return None
    def delete(self,key):
        "删除"
        key=hashlib.md5(key).hexdigest()
        if(self.__type=="simple"):
            if(self.__data.has_key(key)):
                del self.__data[key]
                del self.__timeout[key]
                self.__count=self.__count-1
                self.__log(unicode("删除key:"+key,"UTF-8"))
    def __deleteTimeoutData(self):
        "删除过期数据"
        t=time.time()
        for temp in self.__data:
            if(t>self.__timeout[temp]):
                self.delete(temp)
                
def useHandleMethod(request,response):
    "用户定义的主方法"
    global handleMethod
    handleMethod(request,response)

def outResponseHeader(obj,status,headers):
    "输出header"
    text=status[0]+" "+status[1]+" "+status[2]+"\n"
    for temp in headers:
        text=text+temp[0]+":"+temp[1]+"\n"
    text=text+"\n"
    obj.wfile.write(text)

def outData(obj,data):
    "处理流程结束"
    obj.wfile.write(data)

def getRequestFromUser(string,dict):
    "获取请求的header"
    strs=string.split(": ")
    if(len(strs)==2):
        dict[strs[0]]=strs[1]
    return dict
    
class Request(object):
    "封装请求类"
    def __init__(self,dict,response):
        self.COOKIES={}
        self.SESSIONS={}
        self.method=None
        self.__response=response
        self.__dict=dict
        self.__oldCookies={}
        self.__oldSessions={}
        self.__handleCookie(dict.get("Cookie",""))
        
        #获取session
        global sessionKey,cache
        self.__cache=cache
        self.__sessionKey=sessionKey
        
        if(self.COOKIES.has_key(sessionKey)):
            self.SESSIONS=cache.get(self.COOKIES[sessionKey])
            if(self.SESSIONS==None):
                self.SESSIONS={}
            else:
                self.SESSIONS=json.loads(self.SESSIONS)
        else:
            self.SESSIONS={}
        
        self.method=dict['method']
        self.__getGetArgvs()
        self.__getPostArgvs()
        
    def __handleCookie(self,string):
        "获取cookie"
        cookies=string.split("; ")
        for cookie in cookies:
            temps=cookie.split("=")
            if(len(temps)==2):
                self.COOKIES[temps[0]]=temps[1]
    def __getGetArgvs(self):
        "获取get参数"
        self.GET={}
        self.path=self.__dict['path']
        self.fullPath=self.__dict['path']
        t1=self.__dict['path'].split("?")
        if(len(t1)==2):
            self.path=t1[0]
            t2=re.split(r'[!#]',t1[1])
            if(len(t2)==0):
                t3=t1
            else:
                t3=t2[0]
            t=t3.split("&")
            for temp in t:
                tt=temp.split("=")
                if(len(tt)==2):
                    tt[1]=urllib.unquote(tt[1])
                    self.GET[tt[0]]=tt[1].decode("UTF-8")
    
    def __getPostArgvs(self):
        "获取post参数"
        self.POST={}
        if(self.__dict.has_key("postArgv")):
            temps=str(self.__dict['postArgv']).split("&")
            for temp in temps:
                t=temp.split("=")
                if(len(t)==2):
                    self.POST[t[0]]=t[1].decode("UTF-8")
            
        
    def setSession(self,key,value,timeout=3600):
        "设置session"
        if(not self.COOKIES.has_key(self.__sessionKey)):
            sessionIdValue=str(time.time())
            self.__response.setCookie(self.__sessionKey,sessionIdValue,timeout)
        else:
            sessionIdValue=self.COOKIES[self.__sessionKey]
        self.SESSIONS[key]=value
        self.__cache.set(sessionIdValue,json.dumps(self.SESSIONS))
class Response():
    "封装输出类"
    def __init__(self):
        global sessionKey
        self.META={}
        self.META['server']="webFrame 1.0(bate)"
        self.META['Content-Type']="text/html;charset=utf-8"
        self.__data=""
        self.__status=['http/1.1','200','ok']
        self.__sessionKey=sessionKey
        self.__setcookies=[]
    def write(self,data):
        if(type(data).__name__=="unicode"):
            data=data.encode("UTF-8")
        self.__data=self.__data+str(data)
    def getData(self):
        return self.__data
    def getStatus(self):
        return self.__status
    def setStatus(self,arr):
        self.__status[1]=arr[0]
        self.__status[2]=arr[1]
    def getHeaders(self):
        self.META['Date']=time.strftime("%a, %d %b %Y %H:%M:%S GMT")
        self.META['Content-Length']=str(len(self.__data))
        if(not self.META.has_key('Content-Type')):
            self.META['Content-Type']="text/html"
        arrs=[]
        for temp in self.META:
            arrs.append([temp,self.META[temp]])
        for temp in self.__setcookies:
            end=time.time()+temp[2]
            arrs.append(['Set-Cookie',"%s=%s; expires=%s; Max-Age=%d; Path=%s"%(temp[0],temp[1],time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.localtime(end)),temp[2],temp[3])])
        return arrs
    def setCookie(self,cookieKey,cookieValue,timeout=3600,path="/"):
        "设置cookie"
        self.__setcookies.append([cookieKey,cookieValue,timeout,path])
    
    
#处理类
class MyStreamRequestHandlerr(StreamRequestHandler):
    def __init(self):
        "初始化"
        self.__dict={'ip':self.client_address}
        self.__dict['postArgv']={}
    def __readData(self):
        "读取数据"
        index=0
        while True:
            try:
                data = self.rfile.readline().strip()
                if(data==None or data == ''):
                    if(self.__dict['method']=="POST"):
                        self.__dict['postArgv']=self.rfile.read(int(self.__dict['Content-Length']))
                        self.__dict['postArgv']=urllib.unquote(self.__dict['postArgv'].encode("UTF-8"))
                        break
                    else:
                        break
                    
                if(index==0):
                    datas=data.split(" ")
                    self.__dict['method']=datas[0]
                    self.__dict['path']=datas[1]
                    self.__dict['http_version']=datas[2]
                else:
                    self.__dict=getRequestFromUser(data,self.__dict)
                index=index+1
            except:
                traceback.print_exc()
                break
    def __writeData(self,response):
        "输出数据"
        outResponseHeader(self,response.getStatus(),response.getHeaders())
        outData(self,response.getData())
    def __getRequestAndResponse(self):
        "获取封装类"
        response=Response()
        request=Request(self.__dict,response)
        return request,response
    def handle(self):
        self.__init()
        self.__readData()
        request,response=self.__getRequestAndResponse()
        useHandleMethod(request,response)
        self.__writeData(response)

#初始化函数
def init(method,cacheObj=None):
    global handleMethod,cache
    handleMethod=method
    if(cacheObj==None):
        cache=Cache("simple")
    else:
        cache=cacheObj
    host = "127.0.0.1"
    port = 8000    #端口
    addr = (host, port)
    #监听端口
    server = ThreadingTCPServer(addr, MyStreamRequestHandlerr)
    server.serve_forever()


    
#测试函数    
def testMethod(request,response):
    #response.write(request.COOKIES.get("test","unknow"))
    #response.write(time.time())
    response.setCookie("test","debug")
    request.setSession("abc","123")
    #response.write(request.POST.get("abc","unknow"))
    html="""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <title>欢迎页</title>
            </head>
            <body>
                <p>get参数：{{get}}</p>
                <p>说明：{{text}}</p>
                <form action="" method="post" enctype="multipart/form-data">
                    
                    <input type="file" name="test">
                    <input type="hidden" name="hi" value="123">
                    <input type="submit">
                </form>
            </body>
        </html>
    """
    html=html.replace("{{get}}",request.GET.get("t",u"没有参数！").encode("UTF-8"))
    html=html.replace("{{text}}","webFrame框架制作！")
    response.write(html)
    #response.write(request.GET.get("t",""))
    #response.write("hello world!")
    return response
 
    
"""
-------------------------------------
wsgi开发
-------------------------------------
"""
#wsgi开发
def application(environ,start_response):
    global useHandleMethod
    dict={}
    
    try:
        length=int(environ.get('CONTENT_LENGTH',0))
        body= parse_qs(environ['wsgi.input'].read(length))
        print body
        dict['postArgv']=""
        index=0
        for temp in body:
            if(index!=0):
                dict['postArgv']=dict['postArgv']+"&"
            dict['postArgv']=dict['postArgv']+temp+"="+body[temp][0]
            index=index+1
        print dict['postArgv']
    except:
        dict['postArgv']=""
    dict['path']=environ['PATH_INFO']+"?"+environ['QUERY_STRING']
    dict['method']=environ['REQUEST_METHOD']
    dict['Cookie']=environ.get('HTTP_COOKIE',"")
    
    response=Response()
    request=Request(dict,response)
    useHandleMethod(request,response)
    result=response.getStatus()
    status=result[1]+" "+result[2]
    
    body = response.getData()
    
    result=[]
    results=response.getHeaders()
    for temp in results:
        result.append((temp[0],temp[1]))
    response_headers = result
    start_response(status, response_headers)
    return [body]

    
def wsgiInit(method,cacheObj=None):
    global handleMethod,cache
    handleMethod=method
    if(cacheObj==None):
        cache=Cache("simple")
    else:
        cache=cacheObj
    
    httpd = make_server('localhost', 8000, application)
    httpd.serve_forever()


"""
---------------------
对外接口
---------------------
"""
def useWsgi(environ,start_response,method,cacheObj=None):
    global handleMethod,cache
    handleMethod=method
    if(cacheObj==None):
        cache=Cache("simple")
    else:
        cache=cacheObj
    return application(environ,start_response)
    
if __name__ == "__main__":
    #ThreadingTCPServer
    init(testMethod)
    
    #wsgi
    #wsgiInit(testMethod)

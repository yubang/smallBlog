#coding:UTF-8

import webFrame,lightWeightORM,urlHander,memcache,os

dbInfo={
        'host':'127.0.0.1',
        'port':3306,
        'dbName':'blog',
        'user':'root',
        'password':'root',
    }
cache=memcache.Client(['127.0.0.1:11211'],debug=0)
db=lightWeightORM.Db(dbInfo,True,cache)

def index(request,response):
    global db
    dao=urlHander.UrlHander()
    #dao.setDebug(False)
    dao.setTemplatePath(os.path.dirname(os.path.realpath(__file__))+"/template")
    dao.setClassPath(os.path.dirname(os.path.realpath(__file__))+"/classes")
    dao.load()
    result=dao.dealAccess(request.path,{'db':db,'request':request})
    response.write(result.DATA)
    response.setStatus(result.STATUS)
    for temp in result.META:
        response.META[temp]=result.META[temp]
    
if __name__ == "__main__":
    webFrame.debug=False
    webFrame.wsgiInit(index,cache)

#coding:UTF-8

from urlHander import Action

class Index(Action):
    def index(self):
        "主页"
        page=self._obj['request'].GET.get("page","1")
        page=int(page)
        if(page<=0):
            page=1
            
        dao=self._db.M("blog_content")
        lists=dao.where().order_by("-id").limit((page-1)*5,5).select()
        count=dao.count()
        self._assign("lists",lists)
        
        if(page==1):
            self._assign("lastSign",False)
        else:
            self._assign("lastSign",True)
        
        if((page+1)*5>count):
            self._assign("nextSign",False)
        else:
            self._assign("nextSign",True)
            
        self._assign("last","?page="+str(page-1))
        self._assign("next","?page="+str(page+1))
        self._assign("count",count)
        self._assign("page",page)
        
        self._display()
        return self
        
    def admin(self):
        if(self._obj['request'].SESSIONS.get('admin',None)==None):
            self._redirect("/account")
            return self
        self._display()
        return self
    def account(self):
        if(self._obj['request'].method=="POST"):
            username=self._obj['request'].POST.get('username',None)
            password=self._obj['request'].POST.get('password',None)
            dao=self._db.M("blog_account")
            result=dao.where({'username':username,'password':password}).count()
            if(result==1):
                self._obj['request'].setSession('admin','123',3600)
                self._redirect("/admin")
                return self
            self._assign("message",u"密码错误")
                
        self._obj['request'].setSession('user','0',3600)
        self._display()
        return self
    
    def addBlog(self):
        "添加博客"
        print "\n\n"
        print self._obj['request'].POST
        print "\n\n"
        dao=self._db.M("blog_content")
        result=dao.add({
            'title':self._obj['request'].POST.get('title',None),
            'content':self._obj['request'].POST.get('content',None),
        })
        if(result==None):
            sign=u"添加失败！"
        else:
            sign=u"添加成功！"
        self._assign('sign',sign)
        self._display()
        return self
        
    def about(self):
        self._display()
        return self

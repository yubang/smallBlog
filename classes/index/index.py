#coding:UTF-8

from urlHander import Action

class Index(Action):
    def index(self):
        dao=self._db.M("blog_content")
        lists=dao.where().order_by("-id").select()
        self._assign("lists",lists)
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
            if(self._obj['request'].POST.get('username',None)=="root" and self._obj['request'].POST.get('password',None)=="ewfuewhjfui3284432fhrgfd"):
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

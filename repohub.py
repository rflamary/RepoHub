


import tornado.ioloop
import tornado.web
import tornado.template
import tornado
import tornado.httpserver
import ConfigParser
import codecs
import repos
import time
import subprocess

static_path='www/'
template_path='templates'

    
def load_config(c_file='config.ini'):
    """
    Safe config file loading function
    """
    try:
        config = ConfigParser.ConfigParser()
        config.optionxform = str
        config.readfp(codecs.open(c_file, "r+", "utf8"))
        config=config._sections
        #print config
    except IOError:
        config=None         
    return config  
    
def load_repo_list(cfg):
    lst=[]
    for i,key in enumerate(cfg):
        cftemp=cfg[key]
        temp=dict()
        temp['Name']=key
        temp['config']=cftemp
        temp['index']=i
        temp['type']=cftemp['type']
        temp['path']=cftemp['path']
        temp['repo']=repos.repo[cftemp['type']](cftemp['path'])
        temp['Status']=temp['repo'].get_status_text()
        temp['Actions']=temp['repo'].get_actions_text(i)
        temp['LastModified']=time.ctime(temp['repo'].lastmodified)
        lst.append(temp)
    
    return lst


def update_status(repo_list,distant=0):
    for repo in repo_list:
        if distant:
            repo['repo'].status2()
        else:
            repo['repo'].status()
        repo['Status']=repo['repo'].get_status_text()
        repo['Actions']=repo['repo'].get_actions_text(repo['index'])
        repo['LastModified']=str_time(repo['repo'].lastmodified)
        repo['lm']=repo['repo'].lastmodified
    repo_list.sort(key=lambda k: k['lm'],reverse=True)


def str_time(t):
    return time.strftime('%H:%M:%S %d/%m/%Y',time.localtime(t))

def get_repo(i,repo_list):
    res=[repo for repo in repo_list if repo['index']==i]
    return res[0]
        
def start():
    
    tornado.ioloop.IOLoop.current().start()


def get_label(t,text,n):
    labelbadge_fmt="""<span class="btn btn-{t} btn-xs "><strong>{text}</strong> <span class="badge">{num}</span></span> """
    if n:
        txt=labelbadge_fmt.format(t=t,text=text,num=n)
    else:
        txt=labelbadge_fmt.format(t='success',text=text,num=n)      
    return txt
    
def get_stats(repo_list):
    lastmod=0
    nbmod=0
    toup=0
    tadd=0
      
        
    for repo in repo_list:
        lastmod=max(lastmod,repo['repo'].lastmodified)
        nbmod+=repo['repo'].stats['M']
        toup+=repo['repo'].stats['SM']>0 or repo['repo'].stats['SA']>0
        tadd+=repo['repo'].stats['A']
        
        
         
    return [['Last modified',str_time(lastmod)],
             ['Nb. repos.',len(repo_list)],
             ['Total modified',get_label('warning','Modified',nbmod)],
              ['Total Added',get_label('warning','Added',tadd)],
              [ 'Total to update',get_label('warning','To update',toup)] ]    

class MainHandler(tornado.web.RequestHandler): 
    
    def initialize(self, repo_list,glob):
        
        self.glob = glob
        self.repo_list = repo_list
    
    def get(self):
        update_status(self.repo_list)
        self.render("dashboard.html",content='welcome!',repo_list=self.repo_list,alert=self.glob['message'],atype=self.glob['atype'],stats=get_stats(self.repo_list))
        self.glob['message']=''
        self.glob['atype']='info'

class RepoHandler(tornado.web.RequestHandler): 
    
    def initialize(self, repo_list,glob):
        
        self.glob = glob
        self.repo_list = repo_list
    
    def get(self):
        update_status(self.repo_list)
        index=int(self.get_argument("repo"))
        repo=get_repo(index,self.repo_list)
        self.render("repo2.html",content='welcome!',repo=repo,alert=self.glob['message'],atype=self.glob['atype'],infos=repo['repo'].infoprint,i=index)
        self.glob['message']=''
        self.glob['atype']='info'

        
#class OpenHandler(tornado.web.RequestHandler): 
#    
#    def initialize(self, repo_list,glob):
#        self.glob=glob
#        self.repo_list = repo_list
#    
#    def get(self):
#        update_status(self.repo_list)
#        path=self.get_argument("path")
#        subprocess.Popen("xdg-open {}".format(path), shell=True)
#        self.render("dashboard.html",content='welcome!',repo_list=self.repo_list,alert='<strong>Info</strong>:  Repository folder "{}" opened.'.format(path),atype='info')
#        
#    def post(self):
#        path=self.get_argument("value")
#        subprocess.Popen("xdg-open {}".format(path), shell=True)
#        self.glob['message']=''#'<strong>Info</strong>:  Repository folder "{}" opened.'.format(path)
#        self.glob['atype']='info'
#        self.redirect('/')
        
class ActionHandler(tornado.web.RequestHandler): 
    
    def initialize(self, repo_list,glob):
        self.glob=glob
        self.repo_list = repo_list
    
    def get(self):
        update_status(self.repo_list)
        path=self.get_argument("path")
        subprocess.Popen("xdg-open {}".format(path), shell=True)
        self.render("dashboard.html",content='welcome!',repo_list=self.repo_list,alert='<strong>Info</strong>:  Repository folder "{}" opened.'.format(path),atype='info')
        
    def post(self):
        update_status(self.repo_list)
        action=self.get_argument("action")
        if action=='update':
            index=int(self.get_argument("repo"))
            repo=get_repo(index,self.repo_list)
            message=repo['repo'].update()
            #self.render("output.html",title='Update',alert='',output=message,repo=repo)
            self.glob['message']='Update Repo <strong>{} </strong>: \n <pre class="bg-warning">{}</pre>'.format(repo['Name'],message)
            self.glob['atype']='warning'
            self.redirect('/')
        if action=='status':
            update_status(self.repo_list,1)
            #self.render("output.html",title='Update',alert='',output=message,repo=repo)
            self.glob['message']='<strong>Info: </strong> All distant repository checked'
            self.glob['atype']='info'
            self.redirect('/')    
        if action=='open':
            index=int(self.get_argument("repo"))
            repo=get_repo(index,self.repo_list)
            subprocess.Popen("xdg-open {}".format(repo['path']), shell=True)
            self.glob['message']=''#'<strong>Info</strong>:  Repository folder "{}" opened.'.format(path)
            self.glob['atype']='info'
            self.redirect('/')

        #self.redirect('/')

def callback_repo(repo,action):
    if action=='status2':
        repo['repo'].status2()
        repo['Status']=repo['repo'].get_status_text()
        repo['Actions']=repo['repo'].get_actions_text(repo['index'])
        repo['LastModified']=time.ctime(repo['repo'].lastmodified)
    if action=='status':
        repo['repo'].status()
        repo['Status']=repo['repo'].get_status_text()
        repo['Actions']=repo['repo'].get_actions_text(repo['index'])
        repo['LastModified']=time.ctime(repo['repo'].lastmodified)

def start_periodic_callbacks(repo_list):
    def myfunc(repo,action):
        #print("Callback for Repo: {}, Action: {}".format(repo['Name'],action))
        callback_repo(repo,action)
    lst=[]   
    for repo in repo_list:
        for action,delta in zip(repo['config']['actions'].split(','),[int(t)*1000 for t in repo['config']['periods'].split(',')]):
            print("Repo: {}, Action: {}, Period: {}s".format(repo['Name'],action,delta/1000))
            #f= lambda x=1: (callback_repo(repo,action),myprint(repo['Name'],action) )
            lst.append(tornado.ioloop.PeriodicCallback(lambda repo=repo,action=action:myfunc(repo,action),delta))
            lst[-1].start()

    return lst

    

def make_app():
    
    # load config and repos
    cfg=load_config()
    repo_list=load_repo_list(cfg)
    
    # global informations
    glob=dict()
    glob['message']=''
    glob['atype']='info'
    
    glob['periodic_callbacks']=start_periodic_callbacks(repo_list)
    
    return tornado.web.Application([
        (r"/", MainHandler,{'repo_list':repo_list,'glob':glob}),
  #      (r"/open", OpenHandler,{'repo_list':repo_list,'glob':glob}),
        (r"/repo", RepoHandler,{'repo_list':repo_list,'glob':glob}),
        (r"/action", ActionHandler,{'repo_list':repo_list,'glob':glob}),
        (r"/css/(.*)",tornado.web.StaticFileHandler, {"path": "www/css"},),
        (r"/imgs/(.*)",tornado.web.StaticFileHandler, {"path": "www/imgs"},),
        (r"/js/(.*)",tornado.web.StaticFileHandler, {"path": "www/js"},),
        (r"/fonts/(.*)",tornado.web.StaticFileHandler, {"path": "www/fonts"},),
    ],template_path=template_path)



cfg=load_config()
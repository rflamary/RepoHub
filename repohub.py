


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


def update_status(repo_list):
    for repo in repo_list:
        repo['repo'].status()
        repo['Status']=repo['repo'].get_status_text()
        repo['Actions']=repo['repo'].get_actions_text(repo['index'])
        repo['LastModified']=time.ctime(repo['repo'].lastmodified)
    repo_list.sort(key=lambda k: k['LastModified'],reverse=True)
        
def start():
    
    tornado.ioloop.IOLoop.current().start()

class MainHandler(tornado.web.RequestHandler): 
    
    def initialize(self, repo_list,glob):
        
        self.glob = glob
        self.repo_list = repo_list
    
    def get(self):
        update_status(self.repo_list)
        self.render("dashboard.html",content='welcome!',repo_list=self.repo_list,alert=self.glob['message'],atype=self.glob['atype'])
        self.glob['message']=''
        self.glob['atype']='info'

class RepoHandler(tornado.web.RequestHandler): 
    
    def initialize(self, repo_list,glob):
        
        self.glob = glob
        self.repo_list = repo_list
    
    def get(self):
        update_status(self.repo_list)
        index=int(self.get_argument("repo"))
        repo=self.repo_list[index]
        self.render("repo2.html",content='welcome!',repo=repo,alert=self.glob['message'],atype=self.glob['atype'],infos=repo['repo'].infoprint,i=index)
        self.glob['message']=''
        self.glob['atype']='info'

        
class OpenHandler(tornado.web.RequestHandler): 
    
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
        path=self.get_argument("value")
        subprocess.Popen("xdg-open {}".format(path), shell=True)
        self.glob['message']='<strong>Info</strong>:  Repository folder "{}" opened.'.format(path)
        self.glob['atype']='info'
        self.redirect('/')
        
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
            index=int(self.get_argument("repo")  )
            repo=self.repo_list[index]
            message=repo['repo'].update()
            #self.render("output.html",title='Update',alert='',output=message,repo=repo)
            self.glob['message']='Update Repo <strong>{} </strong>: \n <pre class="bg-warning">{}</pre>'.format(repo['Name'],message)
            self.glob['atype']='warning'
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
        (r"/open", OpenHandler,{'repo_list':repo_list,'glob':glob}),
        (r"/repo", RepoHandler,{'repo_list':repo_list,'glob':glob}),
        (r"/action", ActionHandler,{'repo_list':repo_list,'glob':glob}),
        (r"/css/(.*)",tornado.web.StaticFileHandler, {"path": "www/css"},),
        (r"/imgs/(.*)",tornado.web.StaticFileHandler, {"path": "www/imgs"},),
        (r"/js/(.*)",tornado.web.StaticFileHandler, {"path": "www/js"},),
        (r"/fonts/(.*)",tornado.web.StaticFileHandler, {"path": "www/fonts"},),
    ],template_path=template_path)



cfg=load_config()
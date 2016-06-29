


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
    
    def initialize(self, repo_list):
        self.repo_list = repo_list
    
    def get(self):
        update_status(self.repo_list)
        self.render("dashboard.html",content='welcome!',repo_list=self.repo_list,alert='')

class OpenHandler(tornado.web.RequestHandler): 
    
    def initialize(self, repo_list):
        self.repo_list = repo_list
    
    def get(self):
        update_status(self.repo_list)
        path=self.get_argument("path")
        subprocess.Popen("xdg-open {}".format(path), shell=True)
        self.render("dashboard.html",content='welcome!',repo_list=self.repo_list,alert='<strong>Info</strong>:  Repository folder "{}" opened.'.format(path),atype='info')


def update_status(repo_list):
    for repo in repo_list:
        repo['repo'].status2()
        repo['Status']=repo['repo'].get_status_text()
        repo['Actions']=repo['repo'].get_actions_text(repo['index'])
        repo['LastModified']=time.ctime(repo['repo'].lastmodified)
    repo_list.sort(key=lambda k: k['LastModified'],reverse=True)
    

def make_app():
    cfg=load_config()
    repo_list=load_repo_list(cfg)
    
    
    
    
    
    return tornado.web.Application([
        (r"/", MainHandler,{'repo_list':repo_list}),
        (r"/open", OpenHandler,{'repo_list':repo_list}),
        (r"/css/(.*)",tornado.web.StaticFileHandler, {"path": "www/css"},),
        (r"/js/(.*)",tornado.web.StaticFileHandler, {"path": "www/js"},),
        (r"/fonts/(.*)",tornado.web.StaticFileHandler, {"path": "www/fonts"},),
    ],template_path=template_path)



cfg=load_config()
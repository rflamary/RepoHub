


import tornado.ioloop
import tornado.web
import tornado.template
import tornado
import tornado.httpserver
#import ConfigParser
import configparser
import codecs
import repos
import time
import subprocess
import os.path

static_path=os.path.dirname(os.path.realpath(__file__))+'/www/'
template_path=os.path.dirname(os.path.realpath(__file__))+'/templates'

default_config="""
[Commands]
cmd-list=open,terminal
open-cmd=xdg-open {path}
terminal-cmd=xfce4-terminal --default-working-directory="{path}"

[Visualization]
repo-show-files=A,M, ,D,

[Server]
listen-port=8888
"""


def load_config(c_file='config.ini'):
    """
    Safe config file loading function
    """
    try:
        config = configparser.ConfigParser()
        config.readfp(codecs.open(c_file, "r+", "utf8"))
        cfg=config
        config=config._sections
        #print config
    except IOError:
        config=None
    return config,cfg

def load_repo(i,key,cfgt,cfgtot):
    temp=dict()
    temp['Name']=key
    temp['config']=cfgt
    temp['index']=i
    temp['type']=cfgt['type']
    temp['path']=cfgt['path']
    temp['repo']=repos.lst[cfgt['type']](cfgt['path'],cfgtot)
    temp['Status']=temp['repo'].get_status_text()
    temp['Actions']=temp['repo'].get_actions_text(i)
    temp['LastModified']=time.ctime(temp['repo'].lastmodified)
    return temp

def load_repo_list(cfg,cfgtot):
    lst=[]
    for i,key in enumerate(cfg):
        cftemp=cfg[key]
        temp=load_repo(i,key,cftemp,cfgtot)
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
    tconf=0
    topull=0
    topush=0

    for repo in repo_list:
        lastmod=max(lastmod,repo['repo'].lastmodified)
        nbmod+=repo['repo'].stats['M']
        toup+=repo['repo'].stats['SM']+ repo['repo'].stats['SA']
        tadd+=repo['repo'].stats['A']
        tconf+=repo['repo'].stats['C']
        if repo['type']=='git':
            topull+=repo['repo'].stats['bdelta']
            topush+=repo['repo'].stats['adelta']

    return [['Last modified',str_time(lastmod)],
             ['Nb. repos.',len(repo_list)],
             ['Total modified/added/commits',get_label('warning','Modified',nbmod)+get_label('warning','Added',tadd)+get_label('warning','To push',topush)],
              [ 'Total Conflicts',get_label('danger','Conflicts',tconf)],
              [ 'Total to update/pull',get_label('danger','To update',toup)+get_label('danger','To push',topull)] ]

class MainHandler(tornado.web.RequestHandler):

    def initialize(self, repo_list,glob):

        self.glob = glob
        self.repo_list = repo_list

    def alert(self,message='',atype='atype'):
        self.glob['message']=message
        self.glob['atype']=atype

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
        self.render("repo2.html",content='welcome!',repo=repo,alert=self.glob['message'],atype=self.glob['atype'],infos=repo['repo'].infoprint,glob=self.glob,i=index)
        self.glob['message']=''
        self.glob['atype']='info'

def save_config(path,configobj):
    f=codecs.open(path, "w+", "utf8")
    configobj.write(f)
    f.close()

class ActionHandler(MainHandler):

    def initialize(self, repo_list,glob):
        self.glob=glob
        self.repo_list = repo_list

    def get(self):
        action=self.get_argument("action")
        if action=='update':
            self.redirect('/')
        elif action=='commit':
            index=int(self.get_argument("repo"))
            repo=get_repo(index,self.repo_list)
            self.render("commit.html",content='welcome!',repo=repo,alert=self.glob['message'],atype=self.glob['atype'],infos=repo['repo'].infoprint,i=index)
            self.glob['message']=''
            self.glob['atype']='info'
        elif action=='new':
            self.render("new.html")
            self.glob['message']=''
            self.glob['atype']='info'
        elif action=='settings':
            self.render("settings.html",config=self.glob['config'])
            self.glob['message']=''
            self.glob['atype']='info'
        else:
            self.glob['message']='<strong>Error: </strong> Unknown action '
            self.glob['atype']='danger'
            self.redirect('/')

    def post(self):
        update_status(self.repo_list)
        action=self.get_argument("action",'')
        if action=='update':
            index=int(self.get_argument("repo"))
            repo=get_repo(index,self.repo_list)
            message=repo['repo'].update()
            #self.render("output.html",title='Update',alert='',output=message,repo=repo)
            self.glob['message']=u'Update Repo <strong>{} </strong>: \n <pre class="bg-warning">{}</pre>'.format(repo['Name'],message)
            self.glob['atype']='warning'
            self.redirect('/')
        elif action=='pull':
            index=int(self.get_argument("repo"))
            repo=get_repo(index,self.repo_list)
            message=repo['repo'].pull()
            #self.render("output.html",title='Update',alert='',output=message,repo=repo)
            self.glob['message']=u'Pull Repo <strong>{} </strong>: \n <pre class="bg-warning">{}</pre>'.format(repo['Name'],message)
            self.glob['atype']='warning'
            self.redirect('/')
        elif action=='push':
            index=int(self.get_argument("repo"))
            repo=get_repo(index,self.repo_list)
            message=repo['repo'].push()
            #self.render("output.html",title='Update',alert='',output=message,repo=repo)
            self.glob['message']=u'Push Repo <strong>{} </strong>: \n <pre class="bg-warning">{}</pre>'.format(repo['Name'],message)
            self.glob['atype']='warning'
            self.redirect('/')
        elif action=='status':
            update_status(self.repo_list,1)
            self.glob['message']='<strong>Info: </strong> All distant repository checked'
            self.glob['atype']='info'
            self.redirect('/')
        elif action=='new':
            message='<strong>Info: </strong></br><pre class="bg-info">'
            name=self.get_argument("name")
            path=self.get_argument("path")
            tp=self.get_argument("type")
            actions=self.get_argument("actions")
            periods=self.get_argument("periods")
            if name and not name in self.glob['repos']:
                repos=self.glob['repos']
                repos[name]={}
                repos[name]['path']=path
                repos[name]['type']=tp
                repos[name]['actions']=actions
                repos[name]['periods']=periods
                save_config(self.glob['reposcfg'].filename,self.glob['reposcfg'])
                self.repo_list.append(load_repo(len(self.repo_list),name,repos[name],self.glob['config']))
                start_periodic_callbacks(self.repo_list[-1:])
                message+='Repo {} added succesfully'.format(name)
            elif name:
                message+='Error: Repo name exists'
            else:
                message+='Error: Repo name empty'
            self.glob['message']=message
            self.glob['atype']='info'
            self.redirect('/')
        elif action=='commit':
            index=int(self.get_argument("repo"))
            repo=get_repo(index,self.repo_list)
            textcommit=self.get_argument("commit-text")
            lstfiles=[v[0].decode('utf-8') for k,v in self.request.arguments.items() if 'file' in k]
            outtext=repo['repo'].commit(textcommit,lstfiles)
            self.glob['message']='Commit for <strong> {}</strong> :\n</br><pre class="bg-info"> Commit text:\n {}\nOutput:\n{}</pre>'.format(repo['Name'],textcommit,outtext)
            self.glob['atype']='info'
            self.redirect('/')
        elif action=='open':
            index=int(self.get_argument("repo"))
            repo=get_repo(index,self.repo_list)
            subprocess.Popen(self.glob['config']['Commands']['open-cmd'].format(path=repo['path']), shell=True)
            self.glob['message']=''#'<strong>Info</strong>:  Repository folder "{}" opened.'.format(path)
            self.glob['atype']='info'
            self.redirect('/')
        elif action=='term':
            index=int(self.get_argument("repo"))
            repo=get_repo(index,self.repo_list)
            subprocess.Popen(self.glob['config']['Commands']['terminal-cmd'].format(path=repo['path']), shell=True)
            self.glob['message']=''#'<strong>Info</strong>:  Repository folder "{}" opened.'.format(path)
            self.glob['atype']='info'
            self.redirect('/')
        else:
            self.glob['message']='<strong>Error: </strong> Unknown action '
            self.glob['atype']='danger'
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
    if action=='infos':
        repo['repo'].infos()
        repo['LastModified']=time.ctime(repo['repo'].lastmodified)

def start_periodic_callbacks(repo_list):
    def myfunc(repo,action):
        #print("Callback for Repo: {}, Action: {}".format(repo['Name'],action))
        callback_repo(repo,action)
    lst=[]
    for repo in repo_list:
        for action,delta in zip(repo['config']['actions'].split(','),[int(t)*1000 for t in repo['config']['periods'].split(',')]):
            #print(u"Repo: {}, Action: {}, Period: {}s".format(repo['Name'],action,delta/1000))
            #f= lambda x=1: (callback_repo(repo,action),myprint(repo['Name'],action) )
            lst.append(tornado.ioloop.PeriodicCallback(lambda repo=repo,action=action:myfunc(repo,action),delta))
            lst[-1].start()

    return lst


def check_configfiles():
    configpath=os.path.expanduser('~/.config/repohub/')
    repopath=configpath+'repos.ini'
    cfpath=configpath+'config.ini'
    if not os.path.exists(configpath):
        os.mkdir(configpath)
        open(repopath, 'a').close()
        f=open(cfpath, 'a')
        f.write(default_config)
        f.close()

    return repopath,cfpath


def make_app():

    # load config and repos
    repopath,cfpath=check_configfiles()
    cfg=load_config(cfpath)
    cfgrepos=load_config(repopath)
    repo_list=load_repo_list(cfgrepos[0],cfg[0])

    # global informations
    glob=dict()
    glob['message']=''
    glob['atype']='info'
    glob['repos']=cfgrepos[0]
    glob['config']=cfg[0]
    glob['reposcfg']=cfgrepos[1]
    glob['reposcfg'].filename=repopath
    glob['configcfg']=cfg[1]


    glob['periodic_callbacks']=start_periodic_callbacks(repo_list)

    return tornado.web.Application([
        (r"/", MainHandler,{'repo_list':repo_list,'glob':glob}),
  #      (r"/open", OpenHandler,{'repo_list':repo_list,'glob':glob}),
        (r"/repo", RepoHandler,{'repo_list':repo_list,'glob':glob}),
        (r"/action", ActionHandler,{'repo_list':repo_list,'glob':glob}),
        (r"/css/(.*)",tornado.web.StaticFileHandler, {"path": static_path+"css"},),
        (r"/imgs/(.*)",tornado.web.StaticFileHandler, {"path": static_path+"imgs"},),
        (r"/js/(.*)",tornado.web.StaticFileHandler, {"path": static_path+"js"},),
        (r"/fonts/(.*)",tornado.web.StaticFileHandler, {"path": static_path+"fonts"},),
    ],template_path=template_path),cfg[0]


def start():
    app,config = make_app()
    app.listen(int(config['Server']['listen-port']))
    print('RepoHub starting at address : http://localhost:{}'.format(config['Server']['listen-port']))
    tornado.ioloop.IOLoop.current().start()

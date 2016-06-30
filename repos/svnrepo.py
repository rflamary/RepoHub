

import pysvn
import os
import pprint
import subprocess

convert={'unversioned':'?',
         'ignored':'I',
         'normal':' ',
         'modified':'M',        
         'added':'A',         
         'deleted':'D',      
         'conflicted':'C', 
         'missing':'!', 
         'none':' ', 
}



infoprint_lst={'repos':'Distant repos.',
           'revision':'Revision',
           'commit_revision':'Last commit',
           'url':'URL'}

def get_status(s,path):
    res={}
    res['path']=s.path
    res['fname']=s.path.replace(path,'')
    res['status']=convert[str(s.text_status)]
    res['status2']=convert[str(s.repos_text_status)]
    return res
    

#label_fmt="""<span class="btn btn-{t} btn-xs btn-block"><strong>{text}</strong></span>"""
#labelbadge_fmt="""<span class="btn btn-{t} btn-xs btn-block"><strong>{text}</strong> <span class="badge">{num}</span></span>"""

label_fmt="""<span class="btn btn-{t} btn-xs"><strong>{text}</strong></span> """
labelbadge_fmt="""<span class="btn btn-{t} btn-xs"><strong>{text}</strong> <span class="badge">{num}</span></span> """

button_fmt="""<a href="{url}" class="btn btn-{t} btn-xs" role="button"><strong>{text}</strong></a> """
button_icon_fmt="""<a href="{url}" class="btn btn-{t} btn-xs" role="button"><span class="glyphicon glyphicon-{icon}"></span> <strong>{text}</strong></a> """


button_icon_fmt="""<a href="{url}" class="btn btn-{t} btn-xs" role="button"><span class="glyphicon glyphicon-{icon}"></span> <strong>{text}</strong></a> """

button_icon_fmt_post="""<form class="form-inline hidden" action="{action}" method="post" id="{action}{i}">
<input type="hidden" name="action" value="{action}" /><input type="hidden" name="value" value="{value}" /></form>
<button class="btn btn-{t} btn-xs" type="submit" form="{action}{i}" value="Submit"><span class="glyphicon glyphicon-{icon}"></span> <strong>{text}</strong></button> """

button_icon_fmt_actionpost="""<form class="form-inline hidden" action="action" method="post" id="{action}{i}">
<input type="hidden" name="action" value="{action}" /><input type="hidden" name="value" value="{value}" /><input type="hidden" name="repo" value="{i}" /></form>
<button class="btn btn-{t} btn-xs" type="submit" form="{action}{i}" value="Submit"><span class="glyphicon glyphicon-{icon}"></span> <strong>{text}</strong></button> """


def get_status_text(stats):
    res=''
    if stats['M']>0 :
        res+=labelbadge_fmt.format(t='warning',text='Modified',num=stats['M'])
    if stats['A']>0:
        res+=labelbadge_fmt.format(t='warning',text='Added',num=stats['A'])
    if  stats['SM']>0 or stats['SA']>0 :
        res+=labelbadge_fmt.format(t='danger',text='To update',num= stats['SM'] + stats['SA'])         
    if stats['C']>0:
        res+=labelbadge_fmt.format(t='danger',text='Conflict',num=stats['C'])        
    if res=='':
        res=label_fmt.format(t='success',text='OK')
    return res

def get_actions_text(i,stats):
    #res=button_icon_fmt.format(url='open?path={}'.format(stats['path']),text='Open',t='info',icon='folder-open')
    res=button_icon_fmt_actionpost.format(action='open',i=i,text='Open',t='info',icon='folder-open',value=i)
    res+=button_icon_fmt_actionpost.format(action='update',i=i,value=i,text='Update',t='primary',icon='download')#button_icon_fmt.format(url='action?repo={}&action=update'.format(i),text='Update',t='primary',icon='download')
    if stats['M']>0 or stats['A']>0:
        res+=button_icon_fmt.format(url='action?repo={}&action=commit'.format(i),text='Commit',t='warning',icon='upload')
    return res#"""<div class="btn-toolbar">{}</div>""".format(res)

class repo():
    
    def __init__(self,path):
        self.path=path
        self.l = pysvn.Client()
        self.lastmodified=os.path.getmtime(path)
        self.stat2=[]
        self.infos()
        
    def get_stats(self):
        stats={}
        for key in convert:
            stats[convert[key]]=0
            stats['S'+ convert[key]]=0
        for entry in self.stat:
            stats[entry['status']]+=1
        for entry in self.stat2:
            stats['S'+entry['status2']]+=1            
        stats['path']=self.path
        self.stats=stats

        return stats
        
    def get_status_text(self):
        return get_status_text(self.get_stats())

    def get_actions_text(self,i=0):
        return get_actions_text(i,self.get_stats())
        
    def get_actions_text_large(self,i=0):
        return get_actions_text(i,self.get_stats()).replace('btn-xs','btn-lg')        
        
    def status(self):
        #self.infos()
        ls=self.l.status(self.path,get_all=True)
        self.stat=[get_status(s,self.path) for s in ls]
        self.lastmodified=os.path.getmtime(self.path)
        return self.stat
        
        
    def status2(self):
        self.status()
        ls=self.l.status(self.path,get_all=True,update=True)
        self.stat2=[get_status(s,self.path) for s in ls]
        self.lastmodified=os.path.getmtime(self.path)
        return self.stat2        
        
        
    def update(self):
        global message
        message='Local {path}\n'.format(path=self.path)
#        def notify(event_dict):
#            global message
#            message+=pprint.pformat(event_dict)     
#        self.l.callback_notify = notify
        sp = subprocess.Popen('cd {path}; svn update'.format(path=self.path), shell=True,stdout=subprocess.PIPE)
        out, err = sp.communicate()
        message+=out
        if err:
            message+='\nError\n'+err
        self.status2()
        #self.l.update(self.path)
        return message
        
        
    def infos(self):
        self.status()
        self.linfo=self.l.info(self.path)
        self.localrevision=self.linfo['revision'].number
        infos=dict()
        for key in self.linfo:
            infos[key]=unicode(str(self.linfo[key]))
        infos['localrevision']=self.linfo['revision'].number
        infos['commit_revision']=self.linfo['commit_revision'].number
        infos['copy_from_revision']=self.linfo['copy_from_revision'].number
        infos['revision']=self.linfo['revision'].number
        
        infoprint=dict()
        for key in infoprint_lst:
            infoprint[infoprint_lst[key]]=infos[key]
        infoprint['Local path']=self.path
        infoprint['Labels']=self.get_status_text()

        self.info=infos
        self.infoprint=infoprint
        return self.info
        

        
        

path='/home/rflamary/Documents/Papers/PAMI2015/'
#
test=repo(path)

st=test.infos()
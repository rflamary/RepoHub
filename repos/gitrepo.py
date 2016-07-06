

import os
import subprocess
import xml.etree.cElementTree
import time
import git

convert={'unversioned':'?',
         'ignored':'I',
         'normal':' ',
         'modified':'M',        
         'added':'A',         
         'deleted':'D',      
         'conflicted':'C', 
         'missing':'!', 
         'none':' ', 
         'incomplete':'',          
}



infoprint_lst={'root':'Distant repos.',
           'revision':'Revision',
           'url':'URL'}

    

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
        res+=labelbadge_fmt.format(t='warning',text='Modified',num=stats['M']+stats['D'])
    if stats['A']>0:
        res+=labelbadge_fmt.format(t='warning',text='Added',num=stats['A'])
    if stats['C']>0:
        res+=labelbadge_fmt.format(t='danger',text='Conflicts',num=stats['C'])        
    if  stats['SM']>0 or stats['SA']>0 or stats['SD']>0 :
        res+=labelbadge_fmt.format(t='danger',text='To update',num= stats['SM'] + stats['SA']+ stats['SD'])         
    if stats['C']>0:
        res+=labelbadge_fmt.format(t='danger',text='Conflict',num=stats['C'])        
    if res=='':
        res=label_fmt.format(t='success',text='OK')
    return res
    



def get_actions_text(i,stats,cfg):
    #res=button_icon_fmt.format(url='open?path={}'.format(stats['path']),text='Open',t='info',icon='folder-open')
    res=''
    if 'open' in cfg['Commands']['cmd-list']:
        res+=button_icon_fmt_actionpost.format(action='open',i=i,text='Open',t='info',icon='folder-open',value=i)
    if 'terminal' in cfg['Commands']['cmd-list']:
        res+=button_icon_fmt_actionpost.format(action='term',i=i,text='Terminal',t='info',icon='console',value=i)        
    res+=button_icon_fmt_actionpost.format(action='update',i=i,value=i,text='Update',t='primary',icon='download')#button_icon_fmt.format(url='action?repo={}&action=update'.format(i),text='Update',t='primary',icon='download')
    if stats['M']>0 or stats['A']>0:
        res+=button_icon_fmt.format(url='action?repo={}&action=commit'.format(i),text='Commit',t='warning',icon='upload')
    return res#"""<div class="btn-toolbar">{}</div>""".format(res)

def git_status(rep):
    files=list()
    
    
    stat=rep.git.status('--porcelain')
  

    for entry in stat.split('\n'):
        temp=dict()
        path=entry[3:]
        if len(path.split(' -> '))>1:
            path=path.split(' -> ')[-1]
        
        temp['path']=path
        temp['fname']=path
        temp['status']=entry[1]
        temp['status2']=entry[0]
        files.append(temp)
    
    return files

def git_pull(rep):
    message=rep.git.pull('--no-edit','-v','--stat')
    return message
    
def git_push(rep):
    message=rep.git.push('-v')
    return message


def git_get_branch(rep):
    txt=rep.git.symbolic_ref('-q','HEAD')
    return txt.split('/')[-1]
    
def git_commit_delta(rep,remote=False):
    branch=git_get_branch(rep)
    if remote:
        rep.git.remote('update')
    remote_branch=rep.git.config('--get','branch.{branch}.remote'.format(branch=branch))
    adelta=int(rep.git.rev_list('--count','{remote_branch}..HEAD'.format(remote_branch=remote_branch)))
    bdelta=int(rep.git.rev_list('--count','HEAD..{remote_branch}'.format(remote_branch=remote_branch)))
    return adelta,bdelta

def git_commit(rep,message='',files=[]):
    index = rep.index
    index.add(files)
    res=''
    try:
        res=rep.git.commit('-v','-m',message)
    except git.GitCommandError as err:
        res+='\nError: '+err.__str__()
    
    
    return res

    
def svn_info(path):
    temp=dict()
    sp = subprocess.Popen('svn info --xml'.format(path=path),cwd=path, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = sp.communicate()
    if out:
        e=xml.etree.cElementTree.fromstring(out)
        for child in e[0]:
            temp[child.tag]=child.text
            for child2 in child:
                temp[child2.tag]=child2.text
    temp['localrevision']=int(e[0].find('commit').get('revision'))
    temp['revision']=int(e[0].get('revision'))
    temp['last-change']=time.mktime(time.strptime(temp['date'][:-8],'%Y-%m-%dT%H:%M:%S'))
    del(temp['depth'],temp['repository'],temp['schedule'],temp['wc-info'],temp['commit'])
    return temp

def svn_commit(path,message='',files=[]):
    txtout=''
    if files:
        flist='"'+'" "'.join(files)+'"'
        sp = subprocess.Popen('svn commit --non-interactive {flist} -m "{message}"'.format(path=path,message=message,flist=flist),cwd=path, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = sp.communicate()
        txtout+=out.decode('utf-8')
        if err:
            txtout+='\nError:\n'+err.decode('utf-8')
    else:
        txtout+='No files to commit!'
    return txtout


class repo():
    
    def __init__(self,path,cfg=[]):
        self.path=path
        self.cfg=cfg
        self.lastmodified=os.path.getmtime(path)
        self.repo=git.Repo(path)
        self.stat2=[]
        self.stat=[]
        #self.status()
        #self.infos()
        
        
    def get_stats(self):
        stats={}
        for key in convert:
            stats[convert[key]]=0
            stats['S'+ convert[key]]=0
        #print stats
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
        return get_actions_text(i,self.get_stats(),self.cfg)
        
    def get_actions_text_large(self,i=0):
        return get_actions_text(i,self.get_stats(),self.cfg).replace('btn-xs','btn-lg')        
        
    def status(self):
        self.stat=svn_status(self.path,True)
        return self.stat     
        
    def status2(self):
        self.stat2=svn_status(self.path,True,True)
        return self.stat2   
        
    def get_commit_list(self):
        return [ item for item in svn_status(self.path,False,False) if item['status'] in ['M','A','D']]
        
    def commit(self,message,files):
        return svn_commit(self.path,message,files)
        
        
    def update(self):
        message=svn_update(self.path)
        self.status2()
        return message
        
    def get_last_modif(self):
        self.lastmodified=max(os.path.getmtime(self.path),self.info['last-change'])
        
        
    def infos(self):
        
        #get all infos
        infos=svn_info(self.path)
        
        # handle Info to print
        infoprint=dict()
        for key in infoprint_lst:
            infoprint[infoprint_lst[key]]=infos[key]
        infoprint['Local path']=self.path
        infoprint['Labels']=self.get_status_text()

        self.lastmodified=max(os.path.getmtime(self.path),infos['last-change'])
        self.info=infos
        self.infoprint=infoprint
        return self.info
        

        
        

path="/home/rflamary/PYTHON/RepoHub/"
#rep=git.cmd.Git(path)
rep=git.Repo(path)
status=rep.git.status('--porcelain')
#rp=repo(path)

#st=test.infos()
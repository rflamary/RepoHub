

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



infoprint_lst={'path':'Local path',
           'revision':'Last Commit',
           'author':'Author',
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
    if  stats['adelta']>0  :
        res+=labelbadge_fmt.format(t='warning',text='To push',num=stats['adelta'])
    if  stats['bdelta']>0  :
        res+=labelbadge_fmt.format(t='danger',text='To pull',num=stats['bdelta'])
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
    tpull= 'primary' if stats['bdelta']==0 else 'danger'
    res+=button_icon_fmt_actionpost.format(action='pull',i=i,value=i,text='Pull',t=tpull,icon='download')#button_icon_fmt.format(url='action?repo={}&action=update'.format(i),text='Update',t='primary',icon='download')
    if stats['M']>0 or stats['A']>0 or stats['D']>0:
        res+=button_icon_fmt.format(url='action?repo={}&action=commit'.format(i),text='Commit',t='warning',icon='play-circle')
    if stats['adelta']>0:
        res+=button_icon_fmt_actionpost.format(action='push',i=i,value=i,text='Push',t='warning',icon='upload')
    return res#"""<div class="btn-toolbar">{}</div>""".format(res)

def git_status(rep):
    files=list()


    stat=rep.git.status('--porcelain')

    if stat:
        for entry in stat.split('\n'):
            temp=dict()
            path=entry[3:]
            if len(path.split(' -> '))>1:
                path=path.split(' -> ')[-1]

            temp['path']=path
            temp['fname']=path
            temp['status']=entry[1]
            temp['status2']=entry[0]
            temp['repos-status']=entry[0]
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
    try:
        adelta=int(rep.git.rev_list('--count','{remote_branch}/{branch}..HEAD'.format(remote_branch=remote_branch,branch=branch)))
        bdelta=int(rep.git.rev_list('--count','HEAD..{remote_branch}/{branch}'.format(remote_branch=remote_branch,branch=branch)))
        #adelta=int(rep.git.rev_list('--count','{remote_branch}/{branch}..HEAD'.format(remote_branch=remote_branch,branch=branch)))
        #bdelta=int(rep.git.rev_list('--count','HEAD..{remote_branch}//{branch}'.format(remote_branch=remote_branch,branch=branch)))
    except git.GitCommandError:
        adelta=0
        bdelta=0
        print('Warning: unable to get delta with remote')
    return [adelta,bdelta]

def git_commit_delta2(path,remote=False):
    branch=git_get_branch(rep)
    if remote:
        rep.git.remote('update')
    remote_branch=rep.git.config('--get','branch.{branch}.remote'.format(branch=branch))
    try:
        adelta=int(rep.git.rev_list('--count','{remote_branch}..HEAD'.format(remote_branch=remote_branch)))
        bdelta=int(rep.git.rev_list('--count','HEAD..{remote_branch}'.format(remote_branch=remote_branch)))
    except git.GitCommandError:
        adelta=0
        bdelta=0
        print('Warning: unable to get delta with remote')
    return [adelta,bdelta]



def git_commit(rep,message='',files=[]):
    index = rep.index
    index.add(files)
    try:
        res=rep.git.commit('-v','-m',message)
    except git.GitCommandError as err:
        res='Error: '+err.__str__()
    return res



class repo():

    def __init__(self,path,cfg=[]):
        self.path=path
        self.cfg=cfg
        self.lastmodified=os.path.getmtime(path)
        self.repo=git.Repo(path)
        self.stat=[]
        self.delta=[0,0]
        self.status()
        self.infos()

    def get_stats(self):
        stats={}
        for key in convert:
            stats[convert[key]]=0
            stats['S'+ convert[key]]=0
        #print stats
        for entry in self.stat:
            if not entry['status'] in stats:
                stats[entry['status']]=1
            stats[entry['status']]+=1
        for entry in self.stat:
            if not'S'+ entry['status2'] in stats:
                stats['S'+entry['status2']]=1
            stats['S'+entry['status2']]+=1
        stats['path']=self.path

        stats['adelta']=self.delta[0]
        stats['bdelta']=self.delta[1]

        self.stats=stats
        return stats

    def get_status_text(self):
        return get_status_text(self.get_stats())

    def get_actions_text(self,i=0):
        return get_actions_text(i,self.get_stats(),self.cfg)

    def get_actions_text_large(self,i=0):
        return get_actions_text(i,self.get_stats(),self.cfg).replace('btn-xs','btn-lg')

    def status(self):
        self.delta[0],temp=git_commit_delta(self.repo)
        self.stat=git_status(self.repo)
        self.lastmodified=max(os.path.getmtime(self.path),self.repo.commit().authored_date)
        self.get_stats()
        return self.stat

    def status2(self):
        self.delta=git_commit_delta(self.repo,True)
        self.stat=git_status(self.repo)
        self.lastmodified=max(os.path.getmtime(self.path),self.repo.commit().authored_date)
        self.get_stats()
        return self.stat

    def get_commit_list(self):
        return [ item for item in self.status() if item['status'] in ['M','A','D']]

    def commit(self,message,files):
        return git_commit(self.repo,message,files)


    def pull(self):
        message=git_pull(self.repo)
        self.status2()
        return message

    def push(self):
        message=git_push(self.repo)
        self.status2()
        return message

    def get_last_modif(self):
        self.lastmodified=max(os.path.getmtime(self.path),self.info['last-change'])


    def infos(self):

        #get all infos
        infos={}

        infos['path']=self.path
        infos['author']=self.repo.commit().author.name
        infos['revision']=self.repo.commit().hexsha
        infos['url']=self.repo.git.config('--get','remote.origin.url')

        # handle Info to print
        infoprint=dict()
        for key in infoprint_lst:
            infoprint[infoprint_lst[key]]=infos[key]

        infoprint['Labels']=self.get_status_text()

        self.lastmodified=max(os.path.getmtime(self.path),self.repo.commit().authored_date)
        self.info=infos
        self.infoprint=infoprint
        return self.info





#path="/home/rflamary/PYTHON/RepoHub/"
#rep=git.cmd.Git(path)
#repo=repo(path)
#status=rep.git.status('--porcelain')
#rp=repo(path)

#st=test.infos()

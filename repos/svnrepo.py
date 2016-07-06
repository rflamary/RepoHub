

import os
import subprocess
import xml.etree.cElementTree
import time

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



infoprint_lst={'revision':'Revision',
           'localrevision':'Local revision',
           'author':'Author',
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

def svn_status(path,get_all=True,update=False):
    files=list()
    a=' -v' if get_all else ''
    up=' -u' if update else ''

    sp = subprocess.Popen('svn status --xml --non-interactive {a}{upp}'.format(path=path,a=a,upp=up),cwd=path, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = sp.communicate()
    if out:
        try:
            e=xml.etree.cElementTree.fromstring(out)
            for entry in e[0].findall('entry'):
                temp=dict()
                temp['path']=entry.get('path')
                temp['fname']=entry.get('path')
                wc=entry.find('wc-status')
                temp['status']=convert[wc.get('item')]
                temp['revision']=wc.get('revision')
                cm=entry.find('repos-status')
                if not cm is None:
                    temp['repos-status']=convert[cm.get('item')]
                else:
                    temp['repos-status']=''    
                files.append(temp)
        except xml.etree.ElementTree.ParseError:
            print('Warning: update for {} failed\nOut:\n {}\nError:{}'.format(path,out,err))
    else:
        print('Warning: {}\n Error:\n{}'.format(path,err))
    return files
    
def svn_update(path):
    message='Local path: {path}\n'.format(path=path)
    sp = subprocess.Popen('svn update --non-interactive'.format(path=path),cwd=path, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = sp.communicate()
    message+=out.decode('utf-8')
    if err:
        message+='\nError:\n'+err.decode('utf-8')
    return message
    
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
        
        self.stat2=[]
        self.stat=[]
        self.status()
        self.infos()
        
        
    def get_stats(self):
        stats={}
        for key in convert:
            stats[convert[key]]=0
            stats['S'+ convert[key]]=0
        #print stats
        for entry in self.stat:
            stats[entry['status']]+=1
        for entry in self.stat2:
            stats['S'+entry['repos-status']]+=1            
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
        

        
        

#test=repo(path)

#st=test.infos()
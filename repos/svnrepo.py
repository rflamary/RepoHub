

import os
import subprocess
import xml.etree.cElementTree


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
    if  stats['SM']>0 or stats['SA']>0 :
        res+=labelbadge_fmt.format(t='danger',text='To update',num= stats['SM'] + stats['SA']+ stats['SD'])         
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

def svn_status(path,get_all=True,update=False):
    files=list()
    a=' -v' if get_all else ''
    up=' -u' if update else ''

    sp = subprocess.Popen('cd {path}; svn status --xml {a}{upp}'.format(path=path,a=a,upp=up), shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = sp.communicate()
    if out:
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
    return files
    
def svn_info(path):
    temp=dict()
    sp = subprocess.Popen('cd {path}; svn info --xml'.format(path=path), shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = sp.communicate()
    if out:
        e=xml.etree.cElementTree.fromstring(out)
        for child in e[0]:
            temp[child.tag]=child.text
            for child2 in child:
                temp[child2.tag]=child2.text
    temp['localrevision']=int(e[0].find('commit').get('revision'))
    temp['revision']=int(e[0].get('revision'))
    del(temp['depth'],temp['repository'],temp['schedule'],temp['wc-info'],temp['commit'])
    return temp

def svn_commit(path,message='',files=[]):
    #flist=='"'
    txtout=''
    if files:
        flist='"'+'" "'.join(files)+'"'
        sp = subprocess.Popen('cd {path}; svn commit {flist} -m "{message}"'.format(path=path,message=message,flist=flist), shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = sp.communicate()
        txtout+=out
        if err:
            txtout+='</br>\n<strong>Error</strong>:</br>\n'+err
    else:
        txtout+='No files to commit!'
    #self.l.update(self.path)
    return txtout


class repo():
    
    def __init__(self,path):
        self.path=path
        self.lastmodified=os.path.getmtime(path)
        self.stat2=[]
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
        return get_actions_text(i,self.get_stats())
        
    def get_actions_text_large(self,i=0):
        return get_actions_text(i,self.get_stats()).replace('btn-xs','btn-lg')        
        
    def status(self):
        #self.infos()
        self.stat=svn_status(self.path,True)
        self.lastmodified=os.path.getmtime(self.path)
        return self.stat
        
        
    def status2(self):
        self.status()
        self.stat2=svn_status(self.path,True,True)
        self.lastmodified=os.path.getmtime(self.path)
        return self.stat2   
        
    def get_commit_list(self):
        return [ item for item in svn_status(self.path,False,False) if item['status'] in ['M','A','D']]
        
    def commit(self,message,files):
        return svn_commit(self.path,message,files)
        
        
    def update(self):
        message='Local path: {path}\n'.format(path=self.path)
        sp = subprocess.Popen('cd {path}; svn update'.format(path=self.path), shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = sp.communicate()
        message+=out
        if err:
            message+='</br>\n<strong>Error</strong>:</br>\n'+err
        self.status2()
        #self.l.update(self.path)
        return message
        
        
    def infos(self):
        self.status()
        
        infos=svn_info(self.path)
        
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
#test=repo(path)

#st=test.infos()
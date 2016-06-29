

import pysvn
import os


convert={'unversioned':'?',
         'ignored':'I',
         'normal':' ',
         'modified':'M',        
         'added':'A',         
         'deleted':'D',      
         'conflicted':'C', 
         'missing':'!', 
         'none':'0', 
}



def get_status(s):
    res={}
    res['path']=s.path
    res['status']=convert[str(s.text_status)]
    res['status2']=convert[str(s.repos_text_status)]
    return res
    

#label_fmt="""<span class="btn btn-{t} btn-xs btn-block"><strong>{text}</strong></span>"""
#labelbadge_fmt="""<span class="btn btn-{t} btn-xs btn-block"><strong>{text}</strong> <span class="badge">{num}</span></span>"""

label_fmt="""<span class="btn btn-{t} btn-xs"><strong>{text}</strong></span> """
labelbadge_fmt="""<span class="btn btn-{t} btn-xs "><strong>{text}</strong> <span class="badge">{num}</span></span> """

button_fmt="""<a href="{url}" class="btn btn-{t} btn-xs" role="button"><strong>{text}</strong></a>"""
button_icon_fmt="""<a href="{url}" class="btn btn-{t} btn-xs" role="button"><span class="glyphicon glyphicon-{icon}"></span> <strong>{text}</strong></a>"""



def get_status_text(stats):
    res=''
    if stats['M']>0 :
        res+=labelbadge_fmt.format(t='warning',text='Modified',num=stats['M'])
    if stats['A']>0:
        res+=labelbadge_fmt.format(t='warning',text='Added',num=stats['A'])
    if stats['S ']>0 or stats['SM']>0 or stats['SA']>0 :
        res+=labelbadge_fmt.format(t='danger',text='To update',num=stats['S '] + stats['SM'] + stats['SA'])         
    if stats['C']>0:
        res+=labelbadge_fmt.format(t='danger',text='Conflict',num=stats['C'])        
    if res=='':
        res=label_fmt.format(t='success',text='OK')
    return res

def get_actions_text(i,stats):
    res=button_icon_fmt.format(url='open?path={}'.format(stats['path']),text='Open',t='info',icon='folder-open')
    res+=button_icon_fmt.format(url='action?repo={}&action=update'.format(i),text='Update',t='primary',icon='download')
    if stats['M']>0 or stats['A']>0:
        res+=button_icon_fmt.format(url='action?repo={}&action=commit'.format(i),text='Commit',t='warning',icon='upload')
    return """<div class="btn-toolbar">{}</div>""".format(res)

class repo():
    
    def __init__(self,path):
        self.path=path
        self.l = pysvn.Client()
        self.lastmodified=os.path.getmtime(path)
        self.status()
        self.stat2=[]
        
    def get_stats(self):
        stats={}
        for key in convert:
            stats[convert[key]]=0
            stats['S'+ convert[key]]=0
        for entry in self.stat:
            stats[entry['status']]+=1
        for entry in self.stat2:
            stats['S'+entry['status']]+=1            
        stats['path']=self.path
        self.stats=stats

        return stats
        
    def get_status_text(self):
        return get_status_text(self.get_stats())

    def get_actions_text(self,i=0):
        return get_actions_text(i,self.get_stats())
        
    def status(self):
        ls=self.l.status(self.path,get_all=False)
        self.stat=[get_status(s) for s in ls]
        self.lastmodified=os.path.getmtime(self.path)
        return self.stat
        
    def status2(self):
        ls=self.l.status(self.path,get_all=False,update=True)
        self.stat2=[get_status(s) for s in ls]
        self.lastmodified=os.path.getmtime(self.path)
        return self.stat2        
        
    def infos(self):
        self.info=self.l.info(self.path)
        self.localrevision=self.info['revision'].number
        return self.info

    def update(self):
        temp=self.l.update(self.path)
        self.status()
        self.localrevision=temp[0].number
        return temp[0].number
        
        

path='/home/rflamary/Documents/Papers/PAMI2015/'
#
test=repo(path)
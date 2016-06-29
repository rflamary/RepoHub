

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
}



def get_status(s):
    res={}
    res['path']=s.path
    res['status']=convert["{}".format(s.text_status)]
    return res
    

label_fmt="""<span class="label label-{t}">{text}</span>"""

labelbadge_fmt="""<span class="label label-{t}">{text} <span class="badge">{num}</span></span>"""
button_fmt="""<a href="{url}" class="btn btn-{t}" role="button">{text}</a>"""

def get_status_text(stats):
    res=''
    if stats['M']>0 :
        res+=labelbadge_fmt.format(t='warning',text='Modified',num=stats['M'])
    if stats['A']>0:
        res+=labelbadge_fmt.format(t='warning',text='Added',num=stats['A'])
    if stats['C']>0:
        res+=labelbadge_fmt.format(t='danger',text='conflicted',num=stats['C'])        
    if res=='':
        res=label_fmt.format(t='success',text='OK')
    return res

def get_actions_text(i,stats):
    res=button_fmt.format(url='action?repo={}&action=update'.format(i),text='Update',t='primary')
    if stats['M']>0 or stats['A']>0:
        res+=button_fmt.format(url='action?repo={}&action=commit'.format(i),text='Commit',t='warning')
    return res

class repo():
    
    def __init__(self,path):
        self.path=path
        self.l = pysvn.Client()
        self.status()
        
    def get_stats(self):
        stats={}
        for key in convert:
            stats[convert[key]]=0
        for entry in self.stat:
            stats[entry['status']]+=1
        self.stats=stats
        return stats
        
    def get_status_text(self):
        return get_status_text(self.get_stats())

    def get_actions_text(self,i=0):
        return get_actions_text(i,self.get_stats())
        
    def status(self):
        ls=self.l.status(self.path,get_all=False)
        self.stat=[get_status(s) for s in ls]
        return self.stat
        
    def infos(self):
        self.info=self.l.info(self.path)
        self.localrevision=self.info['revision'].number
        return self.info

    def update(self):
        temp=self.l.update(self.path)
        self.status()
        self.localrevision=temp[0].number
        return temp[0].number
        
        

#path='/home/rflamary/Documents/Papers/ChapitreOptim/'
#
#test=repo(path)
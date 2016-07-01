# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 15:40:56 2016

@author: rflamary
"""


path='/home/rflamary/Documents/Papers/PAMI2015/'
#a=''
#up='-u'
#
#sp = subprocess.Popen('cd {path}; svn status --xml {a}{upp}'.format(path=path,a=a,upp=up), shell=True,stdout=subprocess.PIPE)
#out, err = sp.communicate()
#
#e=xml.etree.cElementTree.fromstring(out)
#
#for entry in e[0].findall('entry'):
#    temp=entry.find('repos-status')
#    print(temp)
#    
#    if not temp is None:
#        print(temp.get('item'))
#        test=temp

temp=dict()
sp = subprocess.Popen('cd {path}; svn info --xml'.format(path=path), shell=True,stdout=subprocess.PIPE)
out, err = sp.communicate()
if out:
    e=xml.etree.cElementTree.fromstring(out)
    for child in e[0]:
        temp[child.tag]=child.text
        for child2 in child:
            temp[child2.tag]=child2.text
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 10:27:16 2016

@author: rflamary
"""




import tornado.ioloop



#actions=['action1','action2']
#deltas=[1000,3000]
#
#lst=[]
#
#def myfunc(action,delta):
#    print("Action: {}, Period: {} s".format(action,delta/1000))
#
#for action,delta in zip(actions,deltas):
##    def f():
##        print("Action: {}, Period: {} s".format(action,delta/1000))
#    f=lambda: myfunc(action,delta)
#    
#    lst.append(f)
#    del f
#    #tornado.ioloop.PeriodicCallback(f,delta).start()
#

lst=[]
for i in range(5):
     f=lambda x: x**i
     lst.append(f)


#def f1():
#    print("Action1")
#
#
#tornado.ioloop.PeriodicCallback(f1,1000).start()
#
#
#def f1():
#    print("Action2")    
#tornado.ioloop.PeriodicCallback(f1,5000).start()
#        
#tornado.ioloop.IOLoop.current().start()

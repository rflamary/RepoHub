




import tornado.ioloop
import tornado.web
import tornado.template
import tornado
import tornado.httpserver

static_path='www/'
template_path='templates'


repo_list=[{'Name':'OTPAMI','Status':'Up to Date','Actions':'Update,Commit,'},{'Name':'Cours/Methodnum','Status':'Up to Date','Actions':'Update,Commit,'}]


def start():
    tornado.ioloop.IOLoop.current().start()

class MainHandler(tornado.web.RequestHandler): 
    
    def get(self):
        self.render("dashboard.html",content='welcome!',repo_list=repo_list)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/css/(.*)",tornado.web.StaticFileHandler, {"path": "www/css"},),
        (r"/js/(.*)",tornado.web.StaticFileHandler, {"path": "www/js"},),
    ],template_path=template_path)


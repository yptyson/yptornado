import os.path
import torndb
import tornado.auth
import tornado.httpserver
import tornado.options
import tornado.web
import unicodedata
import markdown

from tornado.options import define, options

define("port", default=8889, help="run",type=int)
define("mysql_host",default="127.0.0.1:3306",help="db host")
define("mysql_database", default="blog", help="db name")
define("mysql_user", default="root", help="db user")
define("mysql_password", default="123",help="db pw")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/",NewBlogHandler),
            #(r"/entry/([^/]+)", EntryHandler),
            (r"/compose", ComposeHandler),
        ]
        settings=dict(
            blog_title=u"Tyson Blog",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            #ui_modules={"Entry": EntryModule},
            xsrf_cookies=True,
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/auth/login",
            debug=True,
            )
        tornado.web.Application.__init__(self,handlers,**settings)

        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

class NewBlogHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render("new.html", entries="")


class ComposeHandler(BaseHandler):
    def get(self):
        id = self.get_argument("id", None)
        entry = None
        if id:
            entry = self.db.get("SELECT * FROM entries WHERE id = %s", int(id))
        self.render("compose.html", entry=entry)
    def post(self):
        id = self.get_argument("id", None)
        title = self.get_argument("title")
        text = self.get_argument("markdown")
        html = markdown.markdown(text)
        # if id:
        #     return text
        # else:
        #     save()

        #self.redirect("/entry/" + id)
        self.redirect("/" )


def main():
    tornado.options.parse_command_line()
    http_server=tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__=="__main__":
    main()
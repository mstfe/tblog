#coding=utf-8
import os
import markdown
import tornado.autoreload
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.options import define, options


MD_PATH = os.path.join(os.path.dirname(__file__), "md")

define("port", default=8888, help="run on the givn port", type=int)


class MyApplication(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/archive", ArchiveHandler),
            (r"/friendlinks", FriendlinksHandler),
            (r"/recommendablelinks", RecommendablelinksHandler),
            (r"/about", AboutHandler),
            (r"/entry/(.*)", DetailHandler),
            (".*", BaseHandler),
        ]

        settings = dict(
            blog_title="DUST8",
            template_path=os.path.join(os.path.dirname(__file__),
                                       "templates"),
            static_path=os.path.join(os.path.dirname(__file__),
                                     "static"),
            debug=True,
        )

        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    def get_none(self):
        return None


class IndexHandler(BaseHandler):
    def get(self):
        entries = os.listdir(MD_PATH)
        entries.sort(key=lambda x: int(x.replace("-", "")[:8]))
        entries = entries[::-1][:5]
        entries = [filename.replace(".md", "") for filename in entries]
        entriesdict = [splitfilename(filename) for filename in entries]
        self.render("index.html", entriesdict=entriesdict)


class DetailHandler(BaseHandler):
    def get(self, filename):
        file_path = MD_PATH + os.sep + filename + ".md"
        time, title = splitfilename(filename)
        if os.path.isfile(file_path):
            with open(file_path,  encoding="utf-8") as f:
                entry = f.read()
                entry = md(entry)

                self.render("detail.html", title=title, entry=entry)
        else:
            raise tornado.web.HTTPError(404)


class ArchiveHandler(BaseHandler):
    def get(self):
        entries = os.listdir(MD_PATH)
        entries.sort(key=lambda x: int(x.replace("-", "")[:8]))
        entries = entries[::-1]
        entries = [filename.replace(".md", "") for filename in entries]
        entriesdict = [splitfilename(filename) for filename in entries]
        self.render("archive.html", entriesdict=entriesdict)


class FriendlinksHandler(BaseHandler):
    def get(self):
        self.render("friendlinks.html")


class RecommendablelinksHandler(BaseHandler):
    def get(self):
        self.render("recommendablelinks.html")


class AboutHandler(BaseHandler):
    def get(self):
        self.render("about.html")


def md(content):
    return markdown.markdown(content)


def splitfilename(filename):
    filenamelist = filename.split("_")
    return (filenamelist[0], filenamelist[1])


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = MyApplication()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    instance = tornado.ioloop.IOLoop.instance()
    instance.start()

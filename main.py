
import os
import webapp2
import jinja2
import logging
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog_text = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

a = Blog(title="test", blog_text="test text")
a.put()


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)


    def render(self, template, **kw):
        logging.error('looking for a template called ' + template[:100] + 'end of first 100')
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    def get(self):
        self.response.write('Hello world!')

    # def get(self):
    #     self.render("blog.html")

class BlogPage(Handler):
    # def render_blog(self, title="", blog_text="", error=""):
    #     blog_posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
    #     self.render("blog.html", title=title, blog_text=blog_text, error=error, blog_posts=blog_posts)

    def get(self):
        blog_posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        t = jinja_env.get_template("blog.html")
        content = t.render(blog_posts = blog_posts)
        self.response.write(content)
        # self.render_blog()

class NewPost(Handler):

##shoudl i put in get(self, error) to get this to work?
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        blog_text = self.request.get("blog_text")
        have_error = False
        error_title = ""
        error_text = ""


        if not title:
            error_title = "Please provide a title"
            have_error = True

        if not blog_text:
            error_text = "Please provide a blog post"
            have_error = True

        if have_error:
            self.render("newpost.html",title=title, blog_text=blog_text, error_text=error_text, error_title=error_title)

        else:
            a = Blog(title=title, blog_text=blog_text)
            a.put()
            self.redirect('/blog/' + str(a.key().id()))

class ViewPostHandler(Handler):
    def get(self, id):

        post = Blog.get_by_id(int(id))
        if Blog.get_by_id(int(id)):
            # self.render("blog.html", id = Blog.get_by_id(int(id)), blog_posts = blog_posts.title)
            #self.response.out.write("sorry that blog post does not exist")
            t = jinja_env.get_template("post.html")
            content = t.render(post = post)
            self.response.write(content)

        else:
            self.response.out.write("sorry that blog post does not exist")
            # self.response.out.write(Blog.get_by_id)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)

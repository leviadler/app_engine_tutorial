import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

MAIN_PAGE_FOOTER_TEMPLATE = """\
    <form action="/sign?%s" method="post">
      <div>
        <textarea name="content" rows="3" cols="60"></textarea>
      </div>
      <div>
        <input type="submit" value="Sign Guestbook"
      </div>
    </form>
    <hr>
    <form>Guestbook name:
      <input value="%s" name="guestbook_name">
      <input type="submit" value="switch">
    </form>
    <a href="%s">%s</a>
  </body>
 </html>
"""

DEFAULT_GUESTBOOK_NAME = "default_guestbook"

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    # constructs a datastore key for Guestbook entity with guestbook_name
    return ndb.Key("Guestbook", guestbook_name)
    
class Greeting(ndb.Model):
    # Models a individual guestbook entry
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("<html><body>")
        guestbook_name = self.request.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
        
        greetings_query = Greeting.query(ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)
        
        for greeting in greetings:
            if greeting.author:
                self.response.write('<b>%s</b> wrote:' % greeting.author.nickname())
            else:
                self.response.write('An anonymous person wrote:')
            self.response.write('<blockquote>%s</blockquote>' % cgi.escape(greeting.content))
            
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = "Logout"
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = "Login"
            
        # Write the submission form and the footer of the page
        sign_query_params = urllib.urlencode({'guestbook_name' : guestbook_name })
        self.response.write(MAIN_PAGE_FOOTER_TEMPLATE % (sign_query_params, cgi.escape(guestbook_name), url, url_linktext))
        
class Guestbook(webapp2.RequestHandler):
    def post(self):
        self.response.write('<html><body>You wrote:<pre>')
        self.response.write(cgi.escape(self.request.get('content')))
        self.response.write('</pre></body></html>')

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)
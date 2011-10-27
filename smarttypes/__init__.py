"""
====================
Modules
====================

Modules are stored in a global dict, and loaded from the top down. 

Module (x) may load another module (y)

If y then loads x (a cross-reference) it will only have the 
parts of x that were loaded when itself (y) was called by x



====================
This app
====================

mod_wsgi loads wsgi.py 

wsgi.py imports this, which should import everything else
"""

import utils
import model
import controllers
from config import DB_USER, DB_PASSWORD
connection_string = "host=localhost dbname='smarttypes' user='%s' password='%s'" % (DB_USER, DB_PASSWORD)

site_name = 'SmartTypes'
site_mantra = 'a tool for social discovery'
default_title = '%s - %s' % (site_name, site_mantra)
site_description = """
SmartTypes is a social network analysis (SNA) service built to highlight influence and trends within niche communities.
Unlike proprietary SNA services, Smarttypes is open source and accessible. 
Give us a try, sign in with your twitter account, and receive a weekly email highlighting communities, people, and content that interest you. 
"""
site_description = site_description.strip()










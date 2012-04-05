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

import utils  # need this
import model  # need this
import controllers  # need this
from config import DB_USER, DB_PASSWORD
connection_string = "host=localhost dbname='smarttypes' user='%s' password='%s'" % (DB_USER, DB_PASSWORD)

site_name = 'SmartTypes'
site_mantra = 'A tool for social discovery.'
default_title = '%s - %s' % (site_name, site_mantra)
site_description = """
Smarttypes is an open lab for online social network analysis (initially twitter).
We provide automated tools to pull and store social connections and content. 
Our tools respect data provider rate limits and terms of service.
Enough of the boring stuff -- our purpose is to help you explore the great social abyss.
We use a combination of R, Python, and Java packages for data analysis.  
Our collection scripts, and this web app, are built w/ Python.
"""
site_description = site_description.strip()

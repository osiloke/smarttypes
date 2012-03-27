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
site_mantra = 'open data collection and analysis'
default_title = '%s - %s' % (site_name, site_mantra)
site_description = """
SmartTypes is an open and free platform for data collection and analysis.
Configure our data collection monkeys (we only support twitter data collection at the moment),
then pick from a list of state-of-art algos to analyze it.  It's easy and insightful!
We give you pretty visualizations, and a simple "Export to CSV" that complies with our data providers terms of service. 
"""
site_description = site_description.strip()

import sys
import logging

logging.basicConfig(filename='/var/log/catalog.log',level=logging.DEBUG)
#logging.debug('Catalog APP - Udacity FSND P5')

sys.path.insert(0,"/var/www/html/catalog")

from application import app as application

application.secret_key = 'super_secret_key'

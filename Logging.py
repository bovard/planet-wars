import logging

DEBUG = 0
INFO = 0
WARNING = 0
ERROR = 1
CRITICAL = 1

LOG_FILENAME = 'War.log'
if DEBUG or INFO or WARNING or ERROR or CRITICAL: 
  logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG, filemode='w')


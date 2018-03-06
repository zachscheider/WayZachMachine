import os
import sys
import shutil

from subprocess import run, PIPE

# ******************************************************************************
# * TO SET YOUR CONFIGURATION, EDIT THE VALUES BELOW, or use the 'env' command *
# * e.g.                                                                       *
# * env USE_COLOR=True CHROME_BINARY=google-chrome ./archive.py export.html    *
# ******************************************************************************

IS_TTY = sys.stdout.isatty()
USE_COLOR =              os.getenv('USE_COLOR',              str(IS_TTY)        ).lower() == 'true'
SHOW_PROGRESS =          os.getenv('SHOW_PROGRESS',          str(IS_TTY)        ).lower() == 'true'
FETCH_WGET =             os.getenv('FETCH_WGET',             'True'             ).lower() == 'true'
FETCH_WGET_REQUISITES =  os.getenv('FETCH_WGET_REQUISITES',  'True'             ).lower() == 'true'
FETCH_AUDIO =            os.getenv('FETCH_AUDIO',            'False'            ).lower() == 'true'
FETCH_VIDEO =            os.getenv('FETCH_VIDEO',            'False'            ).lower() == 'true'
FETCH_PDF =              os.getenv('FETCH_PDF',              'False'             ).lower() == 'true'
FETCH_SCREENSHOT =       os.getenv('FETCH_SCREENSHOT',       'False'             ).lower() == 'true'
FETCH_FAVICON =          os.getenv('FETCH_FAVICON',          'True'             ).lower() == 'true'
SUBMIT_ARCHIVE =         os.getenv('SUBMIT_ARCHIVE',         'False'             ).lower() == 'true'
RESOLUTION =             os.getenv('RESOLUTION',             '1920,1080'         )
ARCHIVE_PERMISSIONS =    os.getenv('ARCHIVE_PERMISSIONS',    '755'              )
ARCHIVE_DIR =            os.getenv('ARCHIVE_DIR',            '/home/zach/WayZachMachine')
CHROME_BINARY =          os.getenv('CHROME_BINARY',          'chromium-browser' )  # change to google-chrome browser if using google-chrome
WGET_BINARY =            os.getenv('WGET_BINARY',            'wget'             )
WGET_USER_AGENT =        os.getenv('WGET_USER_AGENT',         None)
CHROME_USER_DATA_DIR =   os.getenv('CHROME_USER_DATA_DIR',    None)
TIMEOUT =                int(os.getenv('TIMEOUT',            '60'))
LINK_INDEX_TEMPLATE =    os.getenv('LINK_INDEX_TEMPLATE',    'templates/link_index_fancy.html')
INDEX_TEMPLATE =         os.getenv('INDEX_TEMPLATE',         'templates/index.html')
INDEX_ROW_TEMPLATE =     os.getenv('INDEX_ROW_TEMPLATE',     'templates/index_row.html')

### Output Paths
ROOT_FOLDER = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT_FOLDER)

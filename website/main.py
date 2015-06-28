#Environmental variables - these need to be imported before importing create_app because otherwise they are set after they are needed
import os
import logging
import sys
# root = logging.getLogger()
# root.setLevel(logging.DEBUG)
# ch = logging.StreamHandler(sys.stdout)
# ch.setLevel(logging.DEBUG)
# root.addHandler(ch)
# root.info("Starting logger")

if os.path.exists('.env'):
    # root.info('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from myapp import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


app.debug = True



if __name__ == '__main__':
   
   
    app.run()

    

    


import os
from project import app

__author__ = 'kot'

port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)

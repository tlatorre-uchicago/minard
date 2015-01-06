from flask import Flask

# following the design suggested at http://flask.pocoo.org/docs/patterns/packages/
app = Flask(__name__)

if not app.debug:
    # see http://flask.pocoo.org/docs/errorhandling/
    import logging
    app.logger.addHandler(logging.StreamHandler())

import snoplus_log.views

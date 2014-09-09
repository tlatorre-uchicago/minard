import unittest
from datetime import datetime, timedelta
from minard import app
from minard.views import TRIGGER_NAMES
import random
import json

def build_url(path, kwargs):
    return path + '?' + '&'.join('='.join(map(str,x)) for x in kwargs.items())

class MinardTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_metric(self):
        for i in range(100):
            name = random.choice(TRIGGER_NAMES)
            step = random.randint(1,100)
            now = stop = datetime.now()
            start = stop - timedelta(seconds=5)

            params = {
            'now'   : now.isoformat() + 'Z',
            'stop'  : stop.isoformat() + 'Z',
            'start' : start.isoformat() + 'Z',
            'step'  : step,
            'expr'  : name
            }

            url = build_url('/metric', params)

            rv = self.app.get(url)

            # make sure we get 200 OK
            self.assertEqual(rv.status_code,200)

            data = json.loads(rv.data)

            # make sure we get a list back
            self.assertTrue(isinstance(data['values'],list))

from .db import engine2
from collections import defaultdict

def get_cmos_data():

    conn = engine2.connect()

    result = conn.execute('''SELECT * from cmos order by timestamp DESC limit 9728''')


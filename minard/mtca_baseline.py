from minard.timeseries import INTERVALS, EXPIRE
from redis import Redis
from snotdaq import MTC
import time

#The objective is to store retrieved baseline values into the redis db
class mtca_baselines:
    def __init__(self)

        self.DBToMTC = {"100H":"N100HI","100M":"N100MED","100L":"N100HI",
        "20":"N20","20LB":"N20LB","ESUMH":"ESUMHI","ESUML":"ESUMLO",
        "OWLEH":"OWLEHI","OWLEL":"OWLEHI","OWLN":"OWLN"}
        self.baselines = {"100H":None,"100M":None,"100L":None,"20":None,
        "20LB":None,"ESUMH":None,"ESUML":None,"OWLEL":None,"OWLEH":None,
        "OWLN":None};
        self.mtc = MTC('192.168.80.6') #Connect to MTC server
        self.ConversionFactor = -0.5 #TODO empircally determine this value
    def empty(self):
        for key in self.baselines:
            if self.baselines[key] == None:
                return True
        return False
    def getBaseline(self,name):
        self.mtc.send('threshmon '+self.DBToMTC[name])
        reply = self.mtc.recv()
        #TODO add some fucking error checking and a timeout maybe
        return self.ConvertCorrectionToDrift(int(reply))
        #I think this should be float(reply) actually but idk
        #Tony may or may not have updated this command to do doubles
    def flush(self):
        for key in self.baselines:
            self.baselines[key] = None
    def ConvertCorrectionToDrift(self,correction):
        """The MTCA reads out the amount of baseline correction applied.
            This function uses a calibrated value to convert from correction
            applied to baseline value.
            The conversion is a simple linear scaling"""
        return self.ConversionFactor*correction/1000.0
    def items(self):
        if self.empty():
            for key in self.baselines:
                yield (key,self.getBaseline(key))

def PutBaselinesInDatabase():
    redis = Redis()
    p = redis.pipeline()
    now = int(time.time())
    for interval in INTERVALS:
        p.incrby('ts:%i:%i:baseline-count' % (interval,now//interval),1)
        p.expire('ts:%i:%i:baseline-count' % (interval,now//interval),interval*EXPIRE);
        Baselines = mtca_baselines()
        for name,baseline in Baselines.items():
            key = 'ts:%i:%i:%s' % (interval,now//interval,name+"-Baseline")
            p.incrbyfloat(key,baseline)
            p.expire(key,interval*EXPIRE)
        p.execute()
        Baselines.flush()

if __name__ == '__main__':
    PutBaselinesInDatabase()

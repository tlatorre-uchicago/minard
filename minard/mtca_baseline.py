from minard.timeseries import INTERVALS, EXPIRE
from redis import Redis
from snotdaq import MTC
import time, argparse
#The objective here is to retrieve and store baseline values into a redis db
class mtca_baselines:
    def __init__(self,IP):

        self.DBToMTC = {"100H":"N100HI","100M":"N100MED","100L":"N100HI",
        "20":"N20","20LB":"N20LB","ESUMH":"ESUMHI","ESUML":"ESUMLO",
        "OWLEH":"OWLEHI","OWLEL":"OWLEHI","OWLN":"OWLN"}
        self.baselines = {"100H":None,"100M":None,"100L":None,"20":None,
        "20LB":None,"ESUMH":None,"ESUML":None,"OWLEL":None,"OWLEH":None,
        "OWLN":None};
        self.mtc = MTC(IP) #Connect to MTC server
        self.ConversionFactor = -0.5 #TODO empircally determine this value
    def empty(self):
        for key in self.baselines:
            if self.baselines[key] == None:
                return True
        return False
    def getBaseline(self,name):
        self.mtc.send('threshmon '+self.DBToMTC[name])
        reply = self.mtc.recv()
        try:
            val = int(reply)
        except ValueError:
            print "Could not get baselines"
            return
        return self.convertCorrectionToDrift(val)
        #I think this should be float(reply) actually but idk
        #Tony may or may not have updated this command to do doubles
    def flush(self):
        for key in self.baselines:
            self.baselines[key] = None
    def convertCorrectionToDrift(self,correction):
        """The MTCA reads out the amount of baseline correction applied.
            This function uses a calibrated value to convert from correction
            applied to baseline value.
            The conversion is a simple linear scaling"""
        return self.ConversionFactor*correction/1000.0
    def items(self):
        if self.empty():
            for key in self.baselines:
                yield (key,self.getBaseline(key))

def PutBaselinesInDatabase(IP):
    redis = Redis()
    p = redis.pipeline()
    now = int(time.time())
    Baselines = mtca_baselines(IP)
    #TODO throw an error if connection failed
    for interval in INTERVALS:
        p.incrby('ts:%i:%i:baseline-count' % (interval,now//interval),1)
        p.expire('ts:%i:%i:baseline-count' % (interval,now//interval),interval*EXPIRE);
        for name,baseline in Baselines.items():
            key = 'ts:%i:%i:%s' % (interval,now//interval,name+"-Baseline")
            p.incrbyfloat(key,baseline)
            p.expire(key,interval*EXPIRE)
        p.execute()
        Baselines.flush()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--mtcIP",
    help="Set the IP of the MTC server whence the baselines can be retrieved",
    type=str)
    args = parser.parse_args()
    IP = args.mtcIP if args.mtcIP else 'sbc.sp.snolab.ca'
    PutBaselinesInDatabase(IP)

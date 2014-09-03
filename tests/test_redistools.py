from __future__ import division
import random
import unittest
from redistools import *

def iter_crate(hash, crate):
    for card in range(16):
        for channel in range(32):
            yield hash[crate << 9 | card << 5 | channel]

def iter_card(hash, crate, card):
    for channel in range(32):
        yield hash[crate << 9 | card << 5 | channel]

class TestRedisTools(unittest.TestCase):
    def setUp(self):
        self.hash = {}
        self.hash_crate = {}
        self.hash_card = {}
        for crate in range(20):
            self.hash_crate[crate] = []
            self.hash_card[crate] = {}
            for card in range(16):
                self.hash_card[crate][card] = []
                for channel in range(32):
                    i = (crate << 9) | (card << 5) | channel
                    self.hash[i] = random.choice([1,10,100])
                    self.hash_crate[crate] += [self.hash[i]]
                    self.hash_card[crate][card] += [self.hash[i]]
        redis.delete('spam')
        redis.delete('blah')

        redis.hmset('spam', self.hash)
        redis.set('foo', 2)

    def test_setavgmax(self):
        setavgmax('spam', 'spam:crate:avg', 'spam:crate:max',
                    'spam:card:avg', 'spam:card:max')

        for crate in range(20):
            print 'crate = ', crate
            self.assertAlmostEqual(sum(self.hash_crate[crate])/len(self.hash_crate[crate]),float(redis.hget('spam:crate:avg',crate)))
            self.assertAlmostEqual(max(self.hash_crate[crate]),float(redis.hget('spam:crate:max',crate)))
            for card in range(16):
                print 'card = ', card
                self.assertAlmostEqual(sum(self.hash_card[crate][card])/len(self.hash_card[crate][card]),float(redis.hget('spam:card:avg',crate*512 + card*32)))
                self.assertAlmostEqual(max(self.hash_card[crate][card]),float(redis.hget('spam:card:max',crate*512 + card*32)))
            

    def test_hdivk(self):
        hdivk('result', 'spam', 'foo', self.hash.keys())
        result = redis.hgetall('result')
        for k, v in result.iteritems():
            self.assertAlmostEqual(float(v), self.hash[int(k)]/2)

    def test_hmincr(self):
        hmincr('spam', self.hash.keys())
        hash = redis.hgetall('spam')
        for k, v in hash.iteritems():
            self.assertEqual(int(v),self.hash[int(k)]+1)

    def test_avgcrate(self):
        self.assertEqual(avgcrate('blah',0),None)
        for crate in range(19):
            avg = float(avgcrate('spam',crate))

            vals = [v for v in iter_crate(self.hash,crate) if v != 0]

            self.assertAlmostEqual(avg, sum(vals)/len(vals))

    def test_maxcrate(self):
        self.assertEqual(maxcrate('blah',0),None)
        for crate in range(19):
            max_ = float(maxcrate('spam',crate))

            vals = [v for v in iter_crate(self.hash,crate) if v != 0]

            self.assertAlmostEqual(max_, max(vals))

    def test_maxcard(self):
        self.assertEqual(maxcard('blah',0,0),None)
        crate = random.randint(0,19)
        for card in range(16):
            print('card = %i' % card)
            v = maxcard('spam',crate,card)
            print(type(v))
            max_ = float(v)
            values = [v for v in iter_card(self.hash,crate,card) if v != 0]
            self.assertAlmostEqual(max_, max(values))

    def test_avgcard(self):
        self.assertEqual(avgcard('blah',0,0),None)
        crate = random.randint(0,19)
        for card in range(16):
            v = avgcard('spam',crate,card)
            print(type(v))
            avg = float(v)
            values = [v for v in iter_card(self.hash,crate,card) if v != 0]
            self.assertAlmostEqual(avg, sum(values)/len(values))

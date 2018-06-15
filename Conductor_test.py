from osc import *
from timer import *

OO = OscOut("1.1.1.12", 6000)

def downbeat():
   global n
   OO.sendMessage("/time/downbeat", "DF_test_conductor", n, 90, 4, 4)
   n += 1

T = Timer(2667, downbeat)
n=0
T.start()
from osc import *
from timer import *

OO = OscOut("192.168.0.12", 6000)

def downbeat():
   global n
   OO.sendMessage("/time/downbeat", "DF_test_conductor", n, 64, 4, 4)
   n += 1

T = Timer(3750, downbeat)
n=0
T.start()
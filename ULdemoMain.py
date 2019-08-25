from Urlinie import *
from MIDIInput import *
from time import sleep

MI = MIDIInput()
UL = Urlinie()

MI.setUrlinieReference(UL)
while True:
   sleep(1.0)
   UL.newUrlinie()

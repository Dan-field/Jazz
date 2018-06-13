###############################################################
# Downbeat Sender code by Daniel Field                        #
# sends downbeat messages via OSC                             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# This class is intended to sent downbeat messages
# resembling those the improvisor would receive in
# a Musebot environment

from osc import *
from time import sleep
from threading import Timer
from gui import *
from midi import *

Kill = False
MOut = MidiOut()

# OSC object
O = OscOut("192.168.0.3", 6000)# broadcast port 6000 on the home subnet

def sendDownbeat():
   O.sendMessage("/broadcast/downbeat", "df_DownbeatSender")
   print "sent downbeat"

tempo = 120.0
bpb = 4.0

def masterKill():
   global Kill
   Kill = True

# GUI
d = Display("Master Kill", 270, 50, 10, 10, Color(227, 240, 255))
button1 = Button("Kill", masterKill)
d.add(button1, 10, 10)

# Main
while Kill is False:
   sendDownbeat()
   MOut.note(int(64), 0, 40, 50, 0) # pitch, channel, duration (ms), velocity, start time
   sleep(60.0*bpb/tempo)

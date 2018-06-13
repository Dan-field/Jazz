# version 11a works with the modified timing concept, which is
# slaved to the external downbeat; it does not contain any
# timer or sleep functions itself

from Timekeeper import *
from OSCinput import *
from Player_Motif_v3 import *

kill = False
elapsed = 0.0
synth_delay = 0.25

def timing_loop():
   global TK, kill, t1, elapsed
   if kill is False:
      TK.metronome() # the TK has the Timer function in this version
      count_time = TK.adjusted_16count
      if count_time > 0:
         required_delay = 60.0/count_time
         elapsed += required_delay
      if elapsed > 5.0:
         elapsed = 0.0
         PP.sendAlive()

OO = OSCinput()
PP = MotifPlayer()
OO.setPlayer(PP)

def masterKill():
   global kill
   kill = True

# GUI
d = Display("Master Kill", 540, 100, 20, 20, Color(227, 240, 255))
button1 = Button("Kill", masterKill)
d.add(button1, 20, 20)

# Main
TK=Timekeeper(120, 4, OO) # set up a Timekeeper object
TK.setPlayer(PP)
OO.setTimekeeper(TK)
timing_loop()
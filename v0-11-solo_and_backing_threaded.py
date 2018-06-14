# version 11a works with the modified timing concept, which is
# slaved to the external downbeat; it does not contain any
# timer or sleep functions itself

from threading import Thread
from Timekeeper import *
from OSCinput import *
from Player_Motif_and_Solo import *

kill = False
elapsed = 0.0
synth_delay = 0.25

def timing_loop():
   global TK, kill, t1, elapsed
   if kill is False:
      if OO.timekeeper is not None:
         OO.timekeeper.metronome() # the TK has the Timer function in this version
         count_time = OO.timekeeper.adjusted_16count
         if count_time > 0:
            required_delay = 60.0/count_time
            elapsed += required_delay
         if elapsed > 5.0:
            elapsed = 0.0
            PP.sendAlive()

OO = OSCinput()
PP = MotifPlayer()
OO.setPlayer(PP)

class setup_timer(Thread):
   def run(self):
      global OO, PP
      TK = Timekeeper(120, 4, OO)
      TK.setPlayer(PP)
      OO.setTimekeeper(TK)

def run():
   global OO, PP
   setup_timer().start()
   timing_loop()

def masterKill():
   global kill
   kill = True

# GUI
d = Display("Master Kill", 540, 100, 20, 20, Color(227, 240, 255))
button1 = Button("Kill", masterKill)
d.add(button1, 20, 20)

if __name__ == "__main__":
   run()

# Main
#TK=Timekeeper(120, 4, OO) # set up a Timekeeper object
#TK.setPlayer(PP)
#OO.setTimekeeper(TK)
#timing_loop()
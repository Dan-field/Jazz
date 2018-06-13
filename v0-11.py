from Timekeeper import *
from threading import *
from OSCinput import *
from Player_Motif_v3 import *
from time import sleep

kill = False
elapsed = 0.0
synth_delay = 0.25

# Timer object
def timing_loop():
   global TK, kill, elapsed, synth_delay
   while kill is False:
      TK.metronome()
      count_time = TK.adjusted_16count
      if count_time > 0:
         required_delay = 60.0/count_time
         if required_delay > synth_delay+0.4:
            sleep(required_delay-synth_delay-0.4)
            TK.tap(64)
            sleep(synth_delay)
         else:
            TK.tap(64)
            if required_delay > 0.01:
               sleep(required_delay-0.01)
            sleep(required_delay)
         elapsed += (required_delay)
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
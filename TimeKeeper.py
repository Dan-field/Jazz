###############################################################
# Time Keeper class by Daniel Field                           #
#                                                             #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# This class looks after timing, using a thread
from timer import *

class TimeKeeper:
   def __init__(self):
      """Initialises a TimeKeeper object"""
      # NOTE: 12 ticks per beat
      # NOTE: Timekeeper is like a metronome; it keeps time by 'ticking',
      # BUT it does not track beats, bars, etc - that is done by the Lead Sheet

      # set placeholder for references to other classes
      self.UL = None # placeholder for Urlinie object
      self.LS = None # placeholder for Lead Sheet object
      self.XW = None # placeholder for XMW Writer reference
      self.PP = None # placeholder for Player object

      # set up class variables
      self.tempo = 120
      self.t = Timer(5000.0/self.tempo, self.tick, [], True) # this is (60000.0/tempo)/12 since there are 12 ticks per beat
      self.tempoChanged = False
       
   def tick(self):
      print "TK tick"
      if self.tempoChanged: # the tempo setting has changed since the previous tick
         self.t.setDelay(5.0/self.tempo) # update the new tick delay
         self.tempoChanged = False # reset the changed flag
      self.LS.Tick()

   def getTempo(self):
      return self.tempo

   def setTempo(self, value):
      self.tempo = value
      self.tempoChanged = True

   def kill(self):
      print "stopping Timekeeper timer"
      self.t.stop()

   def restart(self):
      print "starting Timekeeper timer"
      self.t.start()

   def startTimer(self):
      # run the central counter
      print "starting Timekeeper timer"
      self.t.start()
               
   def setLeadSheetReference(self, reference):
      self.LS = reference
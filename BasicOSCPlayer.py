###############################################################
# Basic OSC Player class by Daniel Field                      #
# This player is a super-basic OSC player.                    #
# It sends note events out over OSC                           #
#                                                             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

from NoteSender import *
from random import *
from NotePicker import *
#from gui import *

class BasicOSCPlayer:
   def __init__(self):
      """Initialises a BasicOSCPlayer object"""
      self.sender = NoteSender()
      self.botName = "DF_random-notes-to-MAX"
      self.lastNote = 1
      self.lastVelocity = 0
      self.chordscale = [64, 68, 71, 74]

      self.NP = NotePicker()

   def beat(self, count, tempo):
      note = randint(45, 85)
      velocity = randint(50, 80)
      zippiness = randint(-64, 64)
      pick = self.NP.pickNote(note, "C", self.chordscale)
      self.sender.sendNoteEvent(pick, velocity, zippiness, self.botName)
      self.lastNote = pick
      self.lastVelocity = velocity

   def sendAlive(self):
      self.sender.sendAlive(self.botName)

   def sendSilence(self):
      self.sender.sendNoteEvent(self.lastNote, 0, self.botName)

   def newChordscale(self, newChordscale):
      self.chordscale = self.NP.buildFullRange(newChordscale)

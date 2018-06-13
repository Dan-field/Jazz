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
from Motif import *
#from gui import *

class MotifPlayer:
   def __init__(self):
      """Initialises a BasicOSCPlayer object"""
      self.sender = NoteSender()
      self.botName = "DF_motif-bot_basic"
      self.lastNote = 1
      self.lastVelocity = 0
      self.isMuted = False

      self.NP = NotePicker()
      self.MM = Motif()

      self.chordscale = self.NP.buildFullRange([64, 67, 68, 71, 73, 74])

      self.motif = self.MM.generateNew(2, randint(4, 9))
      self.beat_count = 0
      self.position_count = 0
      self.cycle_count = 0
      self.section_count = 0

   def beat(self, count, tempo):
      if self.beat_count == 0:
         if self.section_count < 3:
            if self.position_count+1 > len(self.motif):
               velocity = 0
               note = 0
            else:
               velocity = randint(50, 80)
               note = self.motif[self.position_count]+67
            self.position_count += 1
            if self.position_count > 7:
               self.position_count = 0
               self.motif = self.MM.jitter(self.motif, 3)
               self.cycle_count += 1
               if self.cycle_count > 7:
                  self.cycle_count = 0
                  self.motif = self.MM.extendUp(self.motif, randint(6, 9))
                  self.section_count += 1
                  if self.section_count == 3:
                     self.motif = self.MM.retrograde(self.motif)
         elif self.section_count < 7:
            velocity = randint(70, 90)
            note = self.motif[self.position_count]+67
            self.position_count += 1
            if self.position_count > 7:
               self.position_count = 0
               self.motif = self.MM.jitter(self.motif, 2)
               self.motif = self.MM.retrograde(self.motif)
               self.cycle_count += 1
               if self.cycle_count > 7:
                  self.cycle_count = 0
                  self.motif = self.MM.invert(self.motif)
                  self.section_count += 1
         else:
            velocity = 0
            note = 0      
      else:
         velocity = 0
         note = 0
      zippiness = randint(0, 45)
      pick = self.NP.pickNote(note, "C", self.chordscale)
      if self.isMuted is True:
         velocity = 0
      self.sender.sendNoteEvent(pick, velocity, zippiness, self.botName)
      self.lastNote = pick
      self.lastVelocity = velocity
      self.beat_count += 1
      if self.beat_count > 1:
         self.beat_count = 0

   def setMute(self, newMute):
      self.isMuted = newMute
      self.sender.sendNoteEvent(self.lastNote, 0, self.botName)

   def sendAlive(self):
      self.sender.sendAlive(self.botName)

   def newChordscale(self, newChordscale):
      self.chordscale = self.NP.buildFullRange(newChordscale)

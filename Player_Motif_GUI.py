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
from gui import *

class MotifPlayer:
   def __init__(self):
      """Initialises a BasicOSCPlayer object"""
      self.sender = NoteSender()
      self.botName = "DF_motif-bot_v2"
      self.lastNote = 1
      self.lastVelocity = 0
      self.isMuted = False
      self.zippiness = 0
      self.legato = False
      self.started = False

      self.NP = NotePicker()
      self.MM = Motif()

      self.chordscale = self.NP.buildFullRange([64, 67, 68, 71, 73, 74])

      self.motif = self.MM.generateNew(2, randint(4, 9))
      self.beat_count = 0
      self.position_count = 0
      self.cycle_count = 0
      self.section_count = 0

      # GUI
      self.d = Display("Player Parameters", 540, 960, 620, 200, Color(227, 240, 255))
      self.checkbox_mute = Checkbox("mute", self.setMute)
      self.checkbox_legato = Checkbox("legato", self.setLegato)
      self.button_restart = Button("restart sequence", self.reStartSequence)
      self.label_zippiness = Label("Zippiness: "+str(int(self.zippiness))+"  ")
      self.slider_zippiness = Slider(HORIZONTAL, 0, 64, self.zippiness, self.setZippiness)
      self.d.add(self.checkbox_mute, 40, 30)
      self.d.add(self.checkbox_legato, 40, 60)
      self.d.add(self.button_restart, 40, 100)
      self.d.add(self.label_zippiness, 40, 140)
      self.d.add(self.slider_zippiness, 40, 170)

   def setLegato(self, newLegato):
      self.legato = newLegato

   def reStartSequence(self):
      self.section_count = 0
      self.cycle_count = 0
      self.motif = self.MM.generateNew(2, randint(4, 9))

   def setZippiness(self, newZippiness):
      self.zippiness = int(newZippiness)
      self.label_zippiness.setText("Zippiness: "+str(int(newZippiness)))

   def beat(self, count, tempo):
      if count == 0:
         self.position_count = 0
         self.started = True
      if self.beat_count == 0 and self.started is True:
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
               self.motif = self.MM.jitter(self.motif, 5)
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
      else: # beat count is 2, which means we're on the "off" 16th
         if self.legato == False:
            velocity = 0
            note = 0
         else:
            velocity = self.lastVelocity
            note = self.lastNote
      if self.position_count == 3 or self.position_count == 7:
         pick = self.NP.pickNote(note, "A", self.chordscale)
      else:
         pick = self.NP.pickNote(note, "C", self.chordscale)
      if self.isMuted is True:
         velocity = 0
      self.sender.sendNoteEvent(pick, velocity, self.zippiness, self.botName)
      self.lastNote = pick
      self.lastVelocity = velocity
      self.beat_count += 1
      if self.beat_count > 1:
         self.beat_count = 0

   def setMute(self, newMute):
      self.isMuted = newMute
      self.sender.sendNoteEvent(self.lastNote, 0, 0, self.botName)
      if newMute == True:
         self.sender.sendMuteStatus(self.botName, 1)
         self.checkbox_mute.check()
      elif newMute == False:
         self.sender.sendMuteStatus(self.botName, 0)
         self.checkbox_mute.uncheck()

   def sendAlive(self):
      self.sender.sendAlive(self.botName)

   def newChordscale(self, newChordscale):
      self.chordscale = self.NP.buildFullRange(newChordscale)

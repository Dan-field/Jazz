###############################################################
# Basic OSC Player class by Daniel Field                      #
# This player is a super-basic OSC player.                    #
# It sends note events out over OSC                           #
#                                                             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# version 3 adds the ability to have some rhythm (in 16th notes)
#
# Rhythms: SSL, LSS, SLS

from NoteSender import *
from random import *
from NotePicker import *
from Motif import *
from gui import *

class MotifPlayer:
   def __init__(self):
      """Initialises a BasicOSCPlayer object"""
      self.sender = NoteSender()
      self.botName = "DF_motif-bot_v3"
      self.lastNote = 1
      self.lastVelocity = 0
      self.isMuted = False
      self.zippiness = 0
      self.legato = False
      self.started = False
      self.hold = 0

      self.NP = NotePicker()
      self.MM = Motif()

      self.chordscale = self.NP.buildFullRange([64, 67, 68, 71, 73, 74])

      self.motif = self.MM.generateNew(3, randint(4, 9), randint(55, 75))
      self.motif_rhythm = self.MM.generateRhythms(3)
      self.motif_function = ["S", "C", "A"]
      self.beat_count = 0
      self.position_count = 0
      self.cycle_count = 0
      self.section_count = 0
      self.toReStart = False

      # GUI
      self.d = Display("Player Parameters", 540, 960, 620, 200, Color(227, 240, 255))
      self.checkbox_mute = Checkbox("mute", self.setMute)
      self.checkbox_legato = Checkbox("legato", self.setLegato)
      self.button_extend = Button("extend sequence", self.extendSequence)
      self.button_restart = Button("restart sequence", self.reStartSequence)
      self.label_zippiness = Label("Zippiness: "+str(int(self.zippiness))+"  ")
      self.slider_zippiness = Slider(HORIZONTAL, 0, 64, self.zippiness, self.setZippiness)
      self.button_allNotesOff = Button("all notes Off", self.allNotesOff)
      self.d.add(self.checkbox_mute, 40, 30)
      self.d.add(self.checkbox_legato, 40, 60)
      self.d.add(self.button_restart, 40, 100)
      self.d.add(self.button_extend, 40, 140)
      self.d.add(self.label_zippiness, 40, 180)
      self.d.add(self.slider_zippiness, 40, 210)
      self.d.add(self.button_allNotesOff, 40, 270)

   def allNotesOff(self):
      self.sender.allNotesOff()

   def setLegato(self, newLegato):
      self.legato = newLegato

   def reStartSequence(self):
      self.toReStart = True

   def makeNewSequence(self):
      self.toReStart = False
      self.section_count = 0
      self.cycle_count = 0
      self.motif = []
      self.motif_rhythm = []
      self.motif = self.MM.generateNew(3, randint(4, 12), randint(55,75))
      self.motif_rhythm = self.MM.generateRhythms(3)

   def extendSequence(self):
      for element in self.MM.generateNew(3, randint(4, 9), self.motif[0]):
         self.motif.append(element)
      for element in self.MM.generateRhythms(3):
         self.motif_rhythm.append(element)
      self.motif_function.append("L")
      self.motif_function.append("C")
      self.motif_function.append("C")

   def setZippiness(self, newZippiness):
      self.zippiness = int(newZippiness)
      self.label_zippiness.setText("Zippiness: "+str(int(newZippiness)))

   def play(self, target, duration, type): # this will become the new 'beat'
      pass

   def beat(self, count, tempo, isLastBeat):
      if count == 0:
         self.position_count = 0
         self.hold = 0
         self.started = True
         velocity = 85
         self.allNotesOff()
      if self.started is True and self.hold == 0:
         note = self.motif[self.position_count]
         duration = self.motif_rhythm[self.position_count]
         function = self.motif_function[self.position_count]
         if count != 0:
            velocity = 60
         self.hold = duration
         self.position_count += 1
         if self.position_count > (len(self.motif)-1):
            self.position_count = 0
         pick = self.NP.pickNote(note, function, self.chordscale)
         if self.isMuted is True:
            velocity = 0
         self.sender.sendNoteEvent(pick, velocity, self.zippiness, self.botName)
         self.lastNote = pick
         self.lastVelocity = velocity
      self.beat_count += 1
      if self.beat_count > 1:
         self.beat_count = 0
      self.hold -= 1
      if self.hold < 0:
         self.hold = 0
      if isLastBeat is True and self.toReStart is True:
         self.makeNewSequence()

   def tap16th(self):
      pass

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

   def newNoteMessage(self, botName, MIDI_No):
      pass

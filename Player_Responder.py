###############################################################
# Respond Player class by Daniel Field                        #
# This player is designed to participate in a responsive      #
# performance.                                                #
#                                                             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################


from NoteSender import *
from random import *
from NotePicker import *
from Motif import *
from gui import *

class RespondPlayer:
   def __init__(self):
      """Initialises a RespondPlayer object"""
      self.sender = NoteSender()
      self.botName = "DF_respond-bot"
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

      self.motif = self.MM.generateNew(3, randint(4, 9), 64)
      self.motif_rhythm = self.MM.generateRhythms(3)
      self.motif_function = ["S", "C", "A"]
      self.beat_count = 0
      self.position_count = 0
      self.cycle_count = 0
      self.section_count = 0
      self.toReStart = False

      # Responder
      self.sequenceLength = 33
      self.otherBotName = None #"PD_w-melo_bot"
      self.otherBotPlaying = False
      self.otherBotSequence = [0 for i in range(self.sequenceLength)]
      self.arrayPosition = 0
      self.delayAmount = int(len(self.otherBotSequence)/2)
      self.pitchShift = 0
      self.counter = 0
      self.isLooping = False

      # GUI
      self.d = Display("Player Parameters", 540, 960, 620, 200, Color(227, 240, 255))
      self.checkbox_mute = Checkbox("mute", self.setMute)
      self.checkbox_legato = Checkbox("legato", self.setLegato)
      self.button_extend = Button("extend sequence", self.extendSequence)
      self.button_restart = Button("restart sequence", self.reStartSequence)
      self.button_bot_reset = Button("reset listento", self.resetOtherBotName)
      self.button_seed = Button("seed sequence", self.seedSequence)
      self.button_up8 = Button("octave Up", self.octaveUp)
      self.button_up5 = Button("fifth Up", self.fifthUp)
      self.button_noShift = Button("no shift", self.noShift)
      self.button_down5 = Button("fifth Down", self.fifthDown)
      self.button_down8 = Button("octave Down", self.octaveDown)
      self.button_jitter = Button("Jitter 5", self.addJitter5)
      self.button_allNotesOff = Button("all notes Off", self.allNotesOff)
      self.checkbox_loop = Checkbox("- Loop -", self.setLooping)
      self.label_zippiness = Label("Zippiness: "+str(int(self.zippiness))+"  ")
      self.label_delayamount = Label("Replay Delay: "+str(int(self.delayAmount))+"  ")
      self.slider_zippiness = Slider(HORIZONTAL, 0, 64, self.zippiness, self.setZippiness)
      self.slider_delay = Slider(HORIZONTAL, 1, len(self.otherBotSequence), self.delayAmount, self.setDelayAmount)
      self.label_botName = Label("Listening to: "+str(self.otherBotName)+"                       ")
      self.d.add(self.checkbox_mute, 40, 30)
      self.d.add(self.checkbox_legato, 40, 60)
      self.d.add(self.button_bot_reset, 40, 100)
      self.d.add(self.button_seed, 40, 140)
      self.d.add(self.label_delayamount, 40, 180)
      self.d.add(self.slider_delay, 40, 210)
      self.d.add(self.button_up8, 310, 30)
      self.d.add(self.button_up5, 310, 70)
      self.d.add(self.button_noShift, 310, 110)
      self.d.add(self.button_down5, 310, 150)
      self.d.add(self.button_down8, 310, 190)
      self.d.add(self.button_jitter, 310, 270)
      self.d.add(self.label_botName, 40, 350)
      self.d.add(self.button_allNotesOff, 40, 270)
      self.d.add(self.checkbox_loop, 40, 420)

   def seedSequence(self):
      self.otherBotSequence = self.MM.generateNew(self.sequenceLength, 16, randint(55, 75))

   def setLooping(self, newStatus):
      if newStatus == True:
         self.isLooping = True
      else:
         self.isLooping = False

   def allNotesOff(self):
      self.sender.allNotesOff()

   def addJitter5(self):
      jittered_copy = self.MM.jitter(self.otherBotSequence, 5)
      self.otherBotSequence = jittered_copy

   def octaveUp(self):
      self.pitchShift = 12

   def fifthUp(self):
      self.pitchShift = 7

   def noShift(self):
      self.pitchShift = 0

   def fifthDown(self):
      self.pitchShift = -7

   def octaveDown(self):
      self.pitchShift = -12

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
      self.motif = self.MM.generateNew(3, randint(4, 9), 64)
      self.motif_rhythm = self.MM.generateRhythms(3)

   def extendSequence(self):
      for element in self.MM.generateNew(3, randint(4, 9), self.motif[0]):
         self.motif.append(element)
      for element in self.MM.generateRhythms(3):
         self.motif_rhythm.append(element)
      self.motif_function.append("L")
      self.motif_function.append("C")
      self.motif_function.append("C")
      print self.motif, self.motif_rhythm, self.motif_function

   def setZippiness(self, newZippiness):
      self.zippiness = int(newZippiness)
      self.label_zippiness.setText("Zippiness: "+str(int(newZippiness)))

   def setDelayAmount(self, newDelay):
      self.delayAmount = int(newDelay)
      self.label_delayamount.setText("Replay Delay: "+str(int(self.delayAmount)))

   def play(self, target, duration, type): # this will become the new 'beat'
      pass

   def beat(self, count, tempo, isLastBeat):
      if count == 0:
         self.beat_count = 0
         velocity = 75
         self.allNotesOff()
      else:
         velocity = 65
      target_index = self.arrayPosition - self.delayAmount
      if target_index < 0:
         target_index += len(self.otherBotSequence)
      note = self.otherBotSequence[target_index]
      function = "C"
      pick = self.NP.pickNote(note, function, self.chordscale)
      if self.isMuted is True:
         velocity = 0
      self.sender.sendNoteEvent(pick, velocity, None, self.botName)
      if self.isLooping is True:
         self.otherBotSequence[self.arrayPosition] = note
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

   def newNoteMessage(self, botName, MIDI_No):
      if self.otherBotName is None and botName != self.botName:
         self.otherBotName = botName
         self.label_botName.setText("Listening to: "+str(self.otherBotName))
      if botName == self.otherBotName and self.isLooping is False:
         self.otherBotSequence[self.arrayPosition] = MIDI_No + self.pitchShift

   def tap16th(self):
      self.arrayPosition += 1
      if self.arrayPosition > len(self.otherBotSequence)-1:
         self.arrayPosition = 0
         self.counter += 1
         if self.counter > 1:
            self.sendAlive()
      self.otherBotSequence[self.arrayPosition] = 0

   def sendAlive(self):
      self.counter = 0
      self.sender.sendAlive(self.botName)
      if all(i == 0 for i in self.otherBotSequence):
         self.otherBotName = None
         self.label_botName.setText("Listening to: "+str(self.otherBotName))

   def resetOtherBotName(self):
      self.otherBotName = None
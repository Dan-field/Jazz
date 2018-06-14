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
      self.botName = "DF_motif-and-solo-bot"
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
      self.motif_function = ["S", "C", "C"]
      self.beat_count = 0
      self.position_count = 0
      self.cycle_count = 0
      self.section_count = 0
      self.toReStart = False
      self.isSoloing = False
      self.base_velocity = 60
      self.playB = False

      # GUI
      self.d = Display("Player Parameters", 540, 960, 620, 200, Color(227, 240, 255))
      self.checkbox_mute = Checkbox("mute", self.setMute)
      self.checkbox_legato = Checkbox("legato", self.setLegato)
      self.button_extend = Button("extend sequence", self.extendSequence)
      self.button_restart = Button("restart sequence", self.reStartSequence)
      self.button_solo = Button(" start soloing ", self.startSoloing)
      self.button_pause = Button(" pause soloing ", self.pauseSoloing)
      self.button_stop = Button(" STOP soloing ", self.stopSoloing)
      self.label_base_velocity = Label("base velocity: "+str(int(self.base_velocity))+"  ")
      self.slider_velocity = Slider(HORIZONTAL, 0, 127, self.base_velocity, self.setBaseVelocity)
      self.button_allNotesOff = Button("all notes Off", self.allNotesOff)
      self.button_up8 = Button("octave Up", self.octaveUp)
      self.button_up5 = Button("fifth Up", self.fifthUp)
      self.button_down5 = Button("fifth Down", self.fifthDown)
      self.button_down8 = Button("octave Down", self.octaveDown)
      self.button_jitter = Button(" jitter ", self.addJitter)
      self.button_b_section = Button(" B-section ", self.bSection)
      self.d.add(self.checkbox_mute, 40, 30)
      self.d.add(self.checkbox_legato, 40, 60)
      self.d.add(self.button_restart, 40, 100)
      self.d.add(self.button_extend, 40, 140)
      self.d.add(self.label_base_velocity, 240, 90)
      self.d.add(self.slider_velocity, 240, 120)
      self.d.add(self.button_solo, 20, 270)
      self.d.add(self.button_allNotesOff, 40, 210)
      self.d.add(self.button_pause, 183, 270)
      self.d.add(self.button_stop, 362, 270)
      self.d.add(self.button_up8, 310, 310)
      self.d.add(self.button_up5, 310, 350)
      self.d.add(self.button_down5, 310, 390)
      self.d.add(self.button_down8, 310, 430)
      self.d.add(self.button_jitter, 40, 310)
      self.d.add(self.button_b_section, 40, 350)

      # solo forms
      self.form1_pitches = self.MM.generateNew(8, 9, 64, 1)
      self.form1_pitches[5] = self.form1_pitches[6]
      self.form1_durations = [1, 1, 1, 1, 1, 1, 2, 8]
      self.form1_functions = ["C", "A", "C", "X", "C", "A", "C", "C"]
      self.form1_velocities = [15, 0, 6, 0, 10, 0, 5, 12]
      self.form1_note_lengths = [0.95, 0.7, 0.9, 0.75, 0.87, 0.6, 1.9, 2.1]
      self.form1_delays = [0, 0, 0, 0, 0, 0, 0, 0]
      self.form2_pitches = self.MM.generateNew(8, 7, 64, 5)
      self.form2_pitches[6] = self.form2_pitches[7]
      self.form2_durations = [1, 1, 1, 1, 1, 1, 2, 8]
      self.form2_functions = ["C", "A", "C", "X", "C", "C", "A", "C"]
      self.form2_velocities = [5, 0, 6, 0, 10, 0, 5, 12]
      self.form2_note_lengths = [0.95, 0.7, 0.9, 0.75, 0.87, 0.6, 1.2, 0.95]
      self.form2_delays = [0, 0, 0, 0, 0, 0, 0, 0]
      self.form3_pitches = self.MM.generateNew(13, 12, 72, 4)
      self.form3_durations = [1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 2]
      self.form3_functions = ["C", "A", "C", "X", "C", "A", "C", "A", "C", "X", "C", "C", "L"]
      self.form3_velocities = [15, 0, 6, 0, 10, 1, 12, 0, 5, 2, 4, 6, 12]
      self.form3_note_lengths = [0.95, 0.95, 0.95, 0.95, 1.95, 1.8, 0.9, 0.86, 0.82, 0.77, 0.7, 0.65, 1.2]
      self.form3_delays = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]   
      form4_pitches = [self.MM.generateNew(4, 4, 68, 4), self.MM.generateNew(4, 4, 66, 4), [64]]
      self.form4_pitches = [item for sublist in form4_pitches for item in sublist]
      self.form4_durations = [1, 1, 1, 1, 1, 1, 1, 1, 8]
      self.form4_functions = ["C", "S", "C", "X", "C", "S", "C", "C", "C"]
      self.form4_velocities = [8, 3, 4, 12, 15, 3, 2, 12, 15]
      self.form4_note_lengths = [0.95, 0.7, 0.9, 0.75, 0.87, 0.6, 0.4, 0.95, 2.4]
      self.form4_delays = [0, 0, 0, 0, 0, 0, 0, 0, 0]
      self.solo_form_count = 0
      self.solo_form_index = 0
      self.current_form_pitches = self.form1_pitches
      self.current_form_durations = self.form1_durations
      self.current_form_functions = self.form1_functions
      self.current_form_velocities = self.form1_velocities
      self.current_form_note_lengths = self.form1_note_lengths
      self.current_form_delays = self.form1_delays

      formB_pitches = [self.MM.generateNew(4, 7, 71, 2), self.MM.generateNew(4, 7, 68, 2), self.MM.generateNew(7, 5, 64, 3)]
      self.formB1_pitches = [item for sublist in formB_pitches for item in sublist]
      self.formB1_durations = [2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 2, 1, 8]
      self.formB1_functions = ["C", "X", "S", "X", "C", "X", "C", "A", "C", "C", "A", "C", "C", "L", "C"]
      self.formB1_velocities = [-5, -5, -5, -5, 0, 0, 0, 0, 5, 0, -5, -10, -10, -15, -10]
      self.formB1_note_lengths = [2.05, 2.05, 2.05, 2.05, 2.05, 2.05, 2.05, 2.05, 1.55, 1.55, 1.05, 1.55, 1.55, 1.05, 4.0]
      self.formB1_delays = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.5, 0.0, 0.0]
      self.formB2_pitches = [i+2 for i in self.formB1_pitches]
      self.formB2_durations = [2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 1, 2, 1, 8]
      self.formB2_functions = ["C", "X", "S", "X", "C", "X", "C", "A", "C", "C", "A", "C", "C", "L", "A"]
      self.formB2_velocities = [5, 5, 5, 5, 0, 0, 0, 0, 5, 0, 5, 10, 10, 15, 10]
      self.formB2_note_lengths = [2.0, 2.0, 2.0, 2.0, 1.95, 1.95, 1.95, 1.8, 1.45, 1.4, 1.0, 1.55, 1.3, 1.05, 7.0]
      self.formB2_delays = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.5, 0.0, 0.0]
     

   def startSoloing(self):
      self.isSoloing = True
      self.hold = 0
      self.started = False

   def pauseSoloing(self):
      self.isSoloing = False
      self.solo_form_index = 0

   def stopSoloing(self):
      self.isSoloing = False
      self.solo_form_count = 0
      self.solo_form_index = 0
      self.current_form_pitches = self.form1_pitches
      self.current_form_durations = self.form1_durations
      self.current_form_functions = self.form1_functions
      self.current_form_velocities = self.form1_velocities

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

   def setBaseVelocity(self, newValue):
      self.base_velocity = int(newValue)
      self.label_base_velocity.setText("base velocity: "+str(int(newValue)))

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
         if self.isSoloing is False:
            note = self.motif[self.position_count]
            duration = self.motif_rhythm[self.position_count]
            function = self.motif_function[self.position_count]
            note_length = 0.85
            delay = 0.0
            if count != 0:
               velocity = self.base_velocity
            self.position_count += 1
            if self.position_count > (len(self.motif)-1):
               self.position_count = 0
         elif self.isSoloing is True:
            note = self.current_form_pitches[self.solo_form_index]
            duration = self.current_form_durations[self.solo_form_index]
            function = self.current_form_functions[self.solo_form_index]
            velocity = self.base_velocity+self.current_form_velocities[self.solo_form_index]
            if velocity > 127:
               velocity = 127
            if velocity < 0:
               velocity = 0
            note_length = self.current_form_note_lengths[self.solo_form_index]+0.1*random()
            delay = self.current_form_delays[self.solo_form_index]
            self.solo_form_index += 1
            if self.solo_form_index > len(self.current_form_pitches)-1:
               self.solo_form_index = 0
               self.nextSoloForm()
         self.hold = duration
         pick = self.NP.pickNote(note, function, self.chordscale)
         if self.isMuted is True:
            velocity = 0
         self.sender.sendNoteEvent(pick, velocity, note_length, self.botName, delay)
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

   def nextSoloForm(self):
      if self.playB is True:
         if self.solo_form_count == 0:
            self.solo_form_count = 1
            self.current_form_pitches = self.formB1_pitches
            self.current_form_durations = self.formB1_durations
            self.current_form_functions = self.formB1_functions
            self.current_form_velocities = self.formB1_velocities
            self.current_form_note_lengths = self.formB1_note_lengths
            self.current_form_delays = self.formB1_delays
         else:
            self.solo_form_count = -1
            self.playB = False
            self.current_form_pitches = self.formB2_pitches
            self.current_form_durations = self.formB2_durations
            self.current_form_functions = self.formB2_functions
            self.current_form_velocities = self.formB2_velocities
            self.current_form_note_lengths = self.formB2_note_lengths
            self.current_form_delays = self.formB2_delays
      else:
         self.solo_form_count += 1
         if self.solo_form_count > 3:
            self.solo_form_count = 0
         if self.solo_form_count == 0:
            self.current_form_pitches = self.form1_pitches
            self.current_form_durations = self.form1_durations
            self.current_form_functions = self.form1_functions
            self.current_form_velocities = self.form1_velocities
            self.current_form_note_lengths = self.form1_note_lengths
            self.current_form_delays = self.form1_delays
         elif self.solo_form_count == 1:
            self.current_form_pitches = self.form2_pitches
            self.current_form_durations = self.form2_durations
            self.current_form_functions = self.form2_functions
            self.current_form_velocities = self.form2_velocities
            self.current_form_note_lengths = self.form2_note_lengths
            self.current_form_delays = self.form2_delays
         elif self.solo_form_count == 2:
            a = choice([1, 2])
            if a == 1:
               self.current_form_pitches = self.form1_pitches
               self.current_form_durations = self.form1_durations
               self.current_form_functions = self.form1_functions
               self.current_form_functions[7] = "L"
               self.current_form_velocities = self.form1_velocities
               self.current_form_velocities[7] = 22
               self.current_form_note_lengths = self.form1_note_lengths
               self.current_form_delays = self.form1_delays
            else:
               self.current_form_pitches = self.form3_pitches
               self.current_form_durations = self.form3_durations
               self.current_form_functions = self.form3_functions
               self.current_form_velocities = self.form3_velocities
               self.current_form_note_lengths = self.form3_note_lengths
               self.current_form_delays = self.form3_delays
         elif self.solo_form_count == 3:
            self.current_form_pitches = self.form4_pitches
            self.current_form_durations = self.form4_durations
            self.current_form_functions = self.form4_functions
            self.current_form_velocities = self.form4_velocities
            self.current_form_note_lengths = self.form4_note_lengths
            self.current_form_delays = self.form4_delays

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

   def octaveUp(self):
      self.current_form_pitches = [i+12 for i in self.current_form_pitches]

   def fifthUp(self):
      self.current_form_pitches = [i+7 for i in self.current_form_pitches]

   def fifthDown(self):
      self.current_form_pitches = [i-7 for i in self.current_form_pitches]

   def octaveDown(self):
      self.current_form_pitches = [i-12 for i in self.current_form_pitches]

   def addJitter(self):
      self.current_form_pitches = self.MM.jitter(self.current_form_pitches, 5)

   def bSection(self):
      self.playB = True
      self.solo_form_count = 0
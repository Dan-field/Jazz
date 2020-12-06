###############################################################
# Note Sender class by Daniel Field                           #
# in version 0-11, this is being modified to sent note events #
# that may be played by another agent (eg MAX)                #
#                                                             #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# This class is intended to sent note messages over OSC
# It will accept note MIDI number and velocity inputs, and
# will send them out over OSC

from osc import *
from midi import *

class NoteSender:
   def __init__(self):
      """Initialises an Note Sender object"""
      #self.oscOutPublic = OscOut("1.1.1.255", 6000)
      #self.oscOutPrivate = OscOut("localhost", 9000) #("192.168.1.7", 33334)

      self.lastPitch = 0
      self.tempo = 120
      self.adjust_to_scale = True
      self.current_scale = []
      self.current_note = -1
      self.default_velocity = 60
      self.this_bar_notes = []
      self.this_bar_times = []
      self.this_bar_count = -1
      # set up lists to hold records of the notes played
      self.playedMIDIno = []
      self.playedTick = []
      self.playedBar = []
      self.ticksPerBar = []

      self.MM = MidiOut()#"OpenJDK Gervill")
      self.XW = None # placeholder for reference to XML Writer
      self.PP = None # placeholder for Player reference

   def setXMLWriterReference(self, reference):
      self.XW = reference

   def setPlayerReference(self, reference):
      self.PP = reference

   def updateBar(self, newBar):
      if self.XW is not None:
         print "NoteSender is using the XW.addBarOfNotes function"
         self.XW.addBarOfNotes(self.this_bar_notes, self.this_bar_times)
         self.this_bar_notes = []
         self.this_bar_times = []
         if newBar == 0:
            self.XW.addMeasureDbl()
         else:
            self.XW.addMeasure()

   def noteOn(self, MIDI_No, fractional_count, velocity=None): # receive a new note, intended as part of a stream of notes. MIDI_No -1 for REST
      self.MM.noteOff(self.current_note)
      if self.adjust_to_scale is True:
         MIDI_No = self.pickClosest(self.current_scale, MIDI_No)
      if velocity is None:
         self.MM.noteOn(MIDI_No, self.default_velocity)
      else:
         self.MM.noteOn(MIDI_No, velocity)
      self.current_note = MIDI_No
      self.this_bar_notes.append(MIDI_No)
      self.this_bar_times.append(fractional_count) # this should be the "48ths" position of the note

   def sendNoteEvent(self, MIDI_No, Vel=None, Note_length=None, botName=None, delay=None):
      MIDI_No = int(MIDI_No+0.5)
      print "Player scale = "+str(self.current_scale)
      if self.adjust_to_scale is True:
         MIDI_No = self.pickClosest(self.current_scale, MIDI_No)
      if Vel is None:
         Vel = 75
      if Note_length is None:
         Note_length = 0.9
      if botName is None:
         botName = "DF_monophonic-note-sender_bot"
      if delay is None:
         delay = 0.0
      duration = int(60000*Note_length/self.tempo)
      if delay != 0.0:
         delay = 15000*delay/self.tempo
      delay = int(delay)
      if Vel != 0 and MIDI_No > 10 and MIDI_No < 120:
         self.MM.note(MIDI_No, delay, duration, Vel, 0, 64)
         #self.oscOutPublic.sendMessage("/event/note", botName, int(MIDI_No))
         self.lastPitch = MIDI_No
      if self.XW is not None:
         self.XW.addNote(MIDI_No)

   def sendNoteShort(self, MIDI_No, Vel=None, Note_length=None):
      if Vel is None:
         Vel = 75
      if Note_length is None:
         Note_length = 0.1
      duration = int(60000*Note_length/self.tempo)
      self.MM.note(MIDI_No, 0, duration, Vel, 0, 64)
      self.lastPitch = MIDI_No

   def sendNoteRaw(self, MIDI_No, Vel=None, Note_length=None):
      if Vel is None:
         Vel = 48
      if Note_length is None:
         Note_length = 0.9
      duration = int(60000*Note_length/self.tempo)
      self.MM.note(MIDI_No, 0, duration, Vel, 0, 64)

   def sendNoteBass(self, MIDI_No, Vel=None, Note_length=None):
      if Vel is None:
         Vel = 55
      if Note_length is None:
         Note_length = 3.75
      duration = int(60000*Note_length/self.tempo)
      self.MM.note(MIDI_No, 0, duration, Vel, 0, 64)

   def sendNoteRawWithTickNo(self, MIDI_No, tick, bar, ticksPerBar, Vel=None, Note_length=None):
      if Vel is None:
         Vel = 75
      if Note_length is None:
         Note_length = 0.9
      duration = int(60000*Note_length/self.tempo)
      self.MM.note(MIDI_No, 0, duration, Vel, 0, 64)
      self.lastPitch = MIDI_No
      self.playedMIDIno.append(MIDI_No)
      self.playedTick.append(tick)
      self.playedBar.append(bar)
      self.ticksPerBar.append(ticksPerBar)

   def showNoteLists(self):
      print "MIDI numbers played: "+str(self.playedMIDIno)
      print "Ticks played: "+str(self.playedTick)
      print "Bars played: "+str(self.playedBar)
      print "------ sending info to MusicXMLWriter ------"
      self.XW.writeMelodyFromTickList(0, self.playedMIDIno, self.playedTick, self.playedBar, self.ticksPerBar)
      self.playedMIDIno = []
      self.playedTick = []
      self.playedBar = []
      self.PP.resetBar()

   def sendNoteLists(self):
      return self.playedMIDIno, self.playedTick, self.playedBar

   def sendAlive(self, botName):
      self.oscOutPublic.sendMessage("/activity/alive", botName)

   def sendMuteStatus(self, botName, muteStatus): # (1 = muted, 0 = not muted)
      self.oscOutPublic.sendMessage("/activity/mutestatus", botName, muteStatus)

   def allNotesOff(self):
      self.MM.allNotesOff()

   def sendTempo(self, newTempo):
      self.tempo = newTempo

   def setScale(self, newScale, rootMIDI):
      print "new scale = "+str(newScale)+", Tonic = "+str(rootMIDI)
      if newScale is None:
         self.current_scale = []
      elif newScale == "":
         self.current_scale = []
      else:
         self.current_scale = self.buildFullScale(newScale, rootMIDI)

   def toggleScaleQuantisation(self, newValue=None):
      if newValue is True:
         self.adjust_to_scale = True
      elif newValue is False:
         self.adjust_to_scale = False
      else:
         if self.adjust_to_scale is True:
            self.adjust_to_scale = False
         else:
            self.adjust_to_scale = True

   def allOctaves(self, MidiNo): # Takes a single MIDI number input and returns a list of that note in all octaves
      octaves = [element*12 for element in range(11)] # produce list [0, 12, 24 ... 120]
      pc = int(MidiNo)%12 # pitch class
      result = []
      for octave in octaves:
         result.append(octave+pc) # this is the pitch class number plus the octave number
      return result

   def buildFullScale(self, scale_values, rootMIDI):
      values = []
      full_scale = []
      rootMIDI = rootMIDI%12
      for value in scale_values:
         value = int(value)%12 # get the pitch class
         if value not in values: # only append it if it's not already in the list
            values.append(value)
      values.sort() # sort them into numerical order
      # with the above preparation, we know the final list will be in order
      octaves = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108]
      for octave in octaves:
         for value in values:
            full_scale.append(octave+value+rootMIDI)
      return full_scale

   def pickClosest(self, notepool, target): # returns the nearest note in the notepool to the target
      # check how far the potential notes are from the target
      if len(notepool) > 0:
         differences = [abs(target - float(note)) for note in notepool]
         # find the closest
         closest = differences.index(min(differences))
         return notepool[closest]
      else:
         return -1

   def setReverb(self, setting):
      self.MM.sendMidiMessage(176, 0, 91, setting) # set the reverb - 176 means control change, 91 means reverb, last value is the level

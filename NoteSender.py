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
      self.oscOutPublic = OscOut("1.1.1.255", 6000)
      self.oscOutPrivate = OscOut("localhost", 9000) #("192.168.1.7", 33334)

      self.lastPitch = 0

      self.MM = MidiOut()

   def sendNoteEvent(self, MIDI_No, Vel=None, Zip=None, botName=None):
      if Vel is None:
         Vel = 65
      if botName is None:
         botName = "DF_monophonic-note-sender_bot"
      if Zip is None:
         Zip = 0
      #self.oscOutPrivate.sendMessage(botName, int(self.lastPitch), 0) #note off
      #self.oscOutPrivate.sendMessage(botName, int(MIDI_No), int(Vel), int(Zip))
      if Vel != 0 and MIDI_No > 10:
         self.MM.note(MIDI_No, 0, 220, Vel, 5, 64)
         self.oscOutPublic.sendMessage("/event/note", botName, int(MIDI_No))
      self.lastPitch = MIDI_No

   def sendAlive(self, botName):
      self.oscOutPublic.sendMessage("/activity/alive", botName)

   def sendMuteStatus(self, botName, muteStatus): # (1 = muted, 0 = not muted)
      self.oscOutPublic.sendMessage("/activity/muteStatus", botName, muteStatus)

   def allNotesOff(self):
      self.MM.allNotesOff()

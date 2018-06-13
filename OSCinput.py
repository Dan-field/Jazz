###############################################################
# OSCinput class by Daniel Field                              #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# This class is intended to handle incoming OSC messages

# VERSION 1 is built entirely for DOWNBEAT messages
# For testing, every message is assumed to be a downbeat (irrespective of content)

from osc import *
from time import time

class OSCinput:
   def __init__(self):
      """Initialises an OSC Input object"""
      self.oscIn = OscIn(6000)
      self.latestDownbeatTime = 0.0
      self.barNo = 0
      self.tempoRx = 120
      self.bpb = 4
      self.division = 4
      self.chordscale = []

      self.timekeeper = None
      self.player = None

      self.oscIn.onInput("/time/downbeat", self.Downbeat) # then string, then bar no, then tempo
      self.oscIn.onInput("/harmony/chordscale", self.Chordscale)
      self.oscIn.onInput("/request/mute", self.MuteMsg)
      self.oscIn.onInput("/event/note", self.IncomingNote)


   def Downbeat(self, message):
      self.latestDownbeatTime = time()
      args = message.getArguments()
      self.barNo = args[1]
      self.tempo = args[2]
      self.bpb = args[3]
      self.division = args[4]
      if self.timekeeper is not None:
         self.timekeeper.setTempo(self.tempo)
         self.timekeeper.setBPB(self.bpb)
         self.timekeeper.setDivisions(self.division)
         self.timekeeper.setDownbeatExternal(self.latestDownbeatTime)

   def Chordscale(self, message):
      args = message.getArguments()
      self.chordscale = []
      for element in args:
         if type(element) is float or type(element) is int:
            self.chordscale.append(int(element))
      if self.player is not None:
         self.player.newChordscale(self.chordscale)

   def MuteMsg(self, message):
      if self.player is not None:
         args = message.getArguments()
         if args[0] == self.player.botName: # it's for us
            if args[1] == 1:
               self.player.setMute(True)
            elif args[1] == 0:
               self.player.setMute(False)

   def IncomingNote(self, message):
      args = message.getArguments()
      if self.player is not None:
         self.player.newNoteMessage(args[0], args[1])

   def getDownbeatTime(self):
      return self.latestDownbeatTime

   def getTempo(self):
      return self.tempo

   def getTimeSig(self):
      return self.bpb, self.division

   def setTimekeeper(self, newTK):
      self.timekeeper = newTK

   def setPlayer(self, newPP):
      self.player = newPP

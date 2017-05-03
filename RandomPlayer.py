###############################################################
# RandomPlayer class by Daniel Field                          #
# refers to the lead sheet and timing to play random notes    #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################



from music import *
from random import *

class RandomPlayer:
   def __init__(self, ls=None):
      """Initialises a RandomPlayer object"""
      self.phr = Phrase()
      self.thisBeatRhythm = [0.5, 0.5]
      self.thisBeatNotes = [56, 57]
      self.thisBeatVelocities = [100, 100]
      self.nextBeatRhythm = [0.5, 0.5]
      self.nextBeatNotes = [58, 59]
      self.nextBeatVelocities = [100, 100]
      
   def playCurrentBeat(self, tempo=None):
      if tempo is None: tempo = 120
      self.phr.setTempo(tempo)
      self.thisBeatRhythm = self.nextBeatRhythm
      self.thisBeatNotes = self.nextBeatNotes
      self.thisBeatVelocities = self.nextBeatVelocities
      self.phr.addNoteList(self.thisBeatNotes, self.thisBeatRhythm, self.thisBeatVelocities)
      Play.midi(self.phr)
      self.phr.empty()
   
   def teeUpNextBeat(self):
      a = 0.5 #random()
      b = 1.0 - a
      c = randint(40, 80)
      d = c+randint(-5, 5)
      e = 100 + randint(-25, 25)
      f = e + randint(-20, 20)
      if f > 127: f=127
      self.nextBeatRhythm = [a, b]
      self.nextBeatNotes = [c, d]
      self.nextBeatVelocities = [e, f]
      

   def beat(self, tempo=None):
      self.playCurrentBeat(tempo)
      self.teeUpNextBeat()
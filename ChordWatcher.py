###############################################################
# ChordWatcher class by Daniel Field                          #
# This 'player' observes the chords and modes in real time    #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################



from music import *
from Analysis import *
from ScaleTheory import *
from random import *

class ChordWatcher:
   def __init__(self, ls=None):
      """Initialises a RandomPlayer object"""
      self.range_top = 81 # the A above middle C
      self.range_bottom = 50 # the A below middle C
      self.target_step = 2.0 # this can be varied - will affect the note choice
      self.near_top = False
      self.near_bottom = False
      self.leadSheet = ls
      self.key, self.key_qual, self.chord, self.chord_qual, self.degrees = ls.getFirstChordInfo()
      self.phr = Phrase()
      self.thisBeatRhythm = [0.5, 0.5]
      self.thisBeatNotes = [56, 57]
      self.thisBeatVelocities = [100, 100]
      self.nextBeatRhythm = [0.5, 0.5]
      self.nextBeatNotes = [58, 59]
      self.nextBeatVelocities = [100, 100]
      self.nextBeatScale = []
      self.nextBeat37 = []
      self.theory = ScaleTheory()

   def rangeLimit(self, full_series):
      return_values = []
      for element in full_series:
         if element >= self.range_bottom and element <= self.range_top:
            return_values.append(element)
      return return_values
      
   def playCurrentBeat(self, tempo=None):
      if tempo is None: tempo = 120
      self.phr.setTempo(tempo)
      Play.midi(self.phr)
   
   def teeUpNextBeat(self):
      nextBar = self.leadSheet.getNextBarChords()
      no_of_chords = len(nextBar)
      a = 0.4 #random()
      b = 1.0 - a
      c, d = self.pickNextBeatNotes()
      e = 100 + randint(-25, 25)
      f = e + randint(-20, 20)
      if f > 127: f=127
      self.nextBeatRhythm = [a, b]
      self.nextBeatNotes = [c, d]
      self.nextBeatVelocities = [e, f]
      self.phr.empty()
      self.thisBeatRhythm = self.nextBeatRhythm
      self.thisBeatNotes = self.nextBeatNotes
      self.thisBeatVelocities = self.nextBeatVelocities
      self.phr.addNoteList(self.thisBeatNotes, self.thisBeatRhythm, self.thisBeatVelocities)

   def pickNextBeatNotes(self):
      nextKey, nextKey_qual, nextChord, nextChord_qual, nextDegrees = self.leadSheet.getNextBeatChordInfo()
      if nextKey == None:
         # there is no next chord - it's the end
         return REST, REST
      else:
         first_note = 63 # set up with scope across this 'else'
         second_note = 64
         if nextKey == 1 and self.nextBeatScale != []:
            # next chord is the same (no chord change) and it's not the first beat
            chord_change = False
         else:
            # next chord is not the same (there is a chord change)
            self.key = nextKey
            self.key_qual = nextKey_qual
            self.chord = nextChord
            self.chord_qual = nextChord_qual
            self.degrees = nextDegrees
            self.nextBeatScale, self.nextBeat37 = self.theory.constructScale(self.key, self.key_qual, self.chord, self.chord_qual, self.degrees, 'new')
            self.nextBeatScale = self.rangeLimit(self.nextBeatScale)
            self.nextBeat37 = self.rangeLimit(self.nextBeat37)
            chord_change = True
         last_note = self.thisBeatNotes[-1]
         second_last_note = self.thisBeatNotes[-2]
         # work out if the last direction was up, default to YES is unsure
         direction_up = True
         if last_note != REST and second_last_note != REST:
            if second_last_note - last_note > 0:
               direction_up = False
         # develop a loose target note
         if direction_up == False:
            loose_target = float(last_note) - self.target_step
         else:
            loose_target = float(last_note) + self.target_step
         # now check if it's a chord change
         if chord_change == True:
            # want to start with a 3 or 7
            # check how far the potential notes are from the loose target
            differences = [abs(loose_target - float(note)) for note in self.nextBeat37]
            # find the closest, and select it as the first note
            closest = differences.index(min(differences))
            # check if near top or bottom (i.e. used first or last element in 37 list)
            if closest == 0:
               self.near_bottom = True
            elif closest == len(self.nextBeat37)-1:
               self.near_top = True
            else:
               self.near_bottom = False
               self.near_top = False
            first_note = self.nextBeat37[closest]
         else:
            # not a chord change, no need to seek out a 3 or 7.
            # follow the same idea but use the whole scale instead of just 3 & 7
            # check how far the potential notes are from the loose target
            differences = [abs(loose_target - float(note)) for note in self.nextBeatScale]
            # find the closest, and select it as the first note
            closest = differences.index(min(differences))
            # check if near top or bottom (i.e. used first or last element in 37 list)
            if closest == 0 or closest == 1:
               self.near_bottom = True
            elif closest == len(self.nextBeatScale)-1 or closest == len(self.nextBeatScale)-2:
               self.near_top = True
            else:
               self.near_bottom = False
               self.near_top = False
            first_note = self.nextBeatScale[closest]
         # now it's time to pick a second note
         # if we're near range top we'll go down, and vice versa
         if self.near_bottom:
            loose_target = float(first_note) + self.target_step
         elif self.near_top:
            loose_target = float(first_note) - (2*self.target_step)
         else:
            loose_target = choice([float(first_note) + self.target_step, float(first_note) - self.target_step])
         # now pick the nearest scale note as above
         differences = [abs(loose_target - float(note)) for note in self.nextBeatScale]
         # find the closest, and select it as the second note
         closest = differences.index(min(differences))
         second_note = self.nextBeatScale[closest]
         return first_note, second_note


   def beat(self, tempo=None):
      self.playCurrentBeat(tempo)
      self.teeUpNextBeat()
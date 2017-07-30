###############################################################
# Analysis class by Daniel Field                              #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# This class is intended to conduct a jazz analysis of the chords
# in a lead sheet to identify chord functions and key centres

from music import *

class ScaleTheory:
   def __init__(self):
      """Initialises a Scale Theory object"""

   def constructScale(self, key, key_qual, chord, chord_qual, degrees, school):
      # build up the modal scale notes
      # note: qualities are always 'major', 'minor' or 'dominant'
      scale_notes, scale_37 = self.selectScale(key_qual, chord_qual, degrees, school)
      complete_scale = self.buildFullScale(self.noteToLowMIDI(chord), scale_notes)
      complete_37 = self.buildFullScale(self.noteToLowMIDI(chord), scale_37)
      return complete_scale, complete_37

   def selectScale(self, key_qual, chord_qual, degrees, school):
      # so-far this function just sticks with major and minor modes.
      # it needs to be expanded to include non-standard combinations
      if chord_qual == 'dominant' and key_qual == 'major':
         # this might not be a standard modal situation
         # just the 5th degree would be expected to be dominant
         if degrees != 5:
            # this is not the standard situation
            # can go crazy with altered scales etc
            if school == 'new':
               return self.getScale('altered'), self.getThreeSeven('altered')
         else:
            # stick with the standard
            return self.getScale('mixolydian'), self.getThreeSeven('mixolydian')
      elif key_qual == 'major' or key_qual == 'dominant':
      # note: we've already exited if it's a dominant chord in a major key.
      # in all other cases, we're still here
      # just use the major modes
         if degrees == 1:
            if school == 'new':
               return self.getScale('lydian'), self.getThreeSeven('lydian')
            else:
               return self.getScale('ionian'), self.getThreeSeven('ionian')
         elif degrees == 2:
            return self.getScale('dorian'), self.getThreeSeven('dorian')
         elif degrees == 3:
            return self.getScale('phrygian'), self.getThreeSeven('phrygian')
         elif degrees == 4:
            return self.getScale('lydian'), self.getThreeSeven('lydian')
         elif degrees == 5:
            return self.getScale('mixolydian'), self.getThreeSeven('mixolydian')
         elif degrees == 6:
            return self.getScale('aeolian'), self.getThreeSeven('aeolian')
         elif degrees == 7:
            return self.getScale('locrian'), self.getThreeSeven('locrian')
         else:
            return None
      elif key_qual == 'minor':
         # use the predominant minor modes
         if degrees == 1:
            if school == 'new':
               return self.getScale('minor_melodic'), self.getThreeSeven('minor_melodic')
            else:
               return self.getScale('aeolian'), self.getThreeSeven('aeolian')
         elif degrees == 2:
            return self.getScale('locrian'), self.getThreeSeven('locrian')
         elif degrees == 3:
            return self.getScale('ionian'), self.getThreeSeven('ionian')
         elif degrees == 4:
            return self.getScale('dorian'), self.getThreeSeven('dorian')
         elif degrees == 5:
            if school == 'new':
               return self.getScale('aeolian_major'), self.getThreeSeven('aeolian_major')
            else:
               return self.getScale('mixolydian'), self.getThreeSeven('mixolydian')
         elif degrees == 6:
            return self.getScale('lydian'), self.getThreeSeven('lydian')
         elif degrees == 7:
            return self.getScale('mixolydian'), self.getThreeSeven('mixolydian')
         else:
            return None
      return None

   def getScale(self, scale_name = None):
      # this function gives 13 scales: the 7 major modes, plus
      # melodic minor ascending, harmonic minor, Aeolean Major, blues, major blues, altered
      if scale_name == 'ionian':
         return [0, 2, 4, 5, 7, 9, 11]
      elif scale_name == 'dorian':
         return [0, 2, 3, 5, 7, 9, 10]
      elif scale_name == 'phrygian':
         return [0, 1, 3, 5, 7, 8, 10]
      elif scale_name == 'lydian':
         return [0, 2, 4, 6, 7, 9, 11]
      elif scale_name == 'mixolydian':
         return [0, 2, 4, 5, 7, 9, 10]
      elif scale_name == 'aeolian':
         return [0, 2, 3, 5, 7, 8, 10]
      elif scale_name == 'locrian':
         return [0, 1, 3, 5, 6, 8, 10]
      elif scale_name == 'minor_harmonic':
         return [0, 2, 3, 5, 7, 8, 11]
      elif scale_name == 'minor_melodic':
         return [0, 2, 3, 5, 7, 9, 11]
      elif scale_name == 'aeolian_major':
         return [0, 2, 4, 5, 7, 8, 10]
      elif scale_name == 'blues':
         return [0, 3, 5, 6, 7, 10]
      elif scale_name == 'blues_major':
         return [0, 2, 3, 4, 7, 9]
      elif scale_name == 'altered':
         return [0, 1, 3, 4, 6, 8, 10]
      else:
         return None

   def getThreeSeven(self, scale_name = None):
      # this function returns the 3rd and 7th degrees
      if scale_name == 'ionian':
         return [4, 11]
      elif scale_name == 'dorian':
         return [3, 10]
      elif scale_name == 'phrygian':
         return [3, 10]
      elif scale_name == 'lydian':
         return [4, 11]
      elif scale_name == 'mixolydian':
         return [4, 10]
      elif scale_name == 'aeolian':
         return [3, 10]
      elif scale_name == 'locrian':
         return [3, 10]
      elif scale_name == 'minor_harmonic':
         return [3, 11]
      elif scale_name == 'minor_melodic':
         return [3, 11]
      elif scale_name == 'aeolian_major':
         return [4, 10]
      elif scale_name == 'blues':
         return [3, 10]
      elif scale_name == 'blues_major':
         return [4, 9]
      elif scale_name == 'altered':
         return [3, 10]
      else:
         return None

   def noteToLowMIDI(self, note_name = None):
      # returns a low octave MIDI number
      if note_name == 'A':
         return 9
      elif note_name == 'AS' or note_name == 'BF':
         return 10
      elif note_name == 'B':
         return 11
      elif note_name == 'C':
         return 12
      elif note_name == 'CS' or note_name == 'DF':
         return 13
      elif note_name == 'D':
         return 14
      elif note_name == 'DS' or note_name == 'EF':
         return 15
      elif note_name == 'E':
         return 16
      elif note_name == 'F':
         return 17
      elif note_name == 'FS' or note_name == 'GF':
         return 18
      elif note_name == 'G':
         return 19
      elif note_name == 'GS' or note_name == 'AF':
         return 20

   def buildFullScale(self, starting_note, scale_values):
      full_scale = []
      octaves = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108]
      for octave in octaves:
         for value in scale_values:
            full_scale.append(starting_note+octave+value)
      return full_scale
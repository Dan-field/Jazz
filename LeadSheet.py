###############################################################
# LeadSheet class by Daniel Field                             #
# derived from Improfunctions                                 #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# This class is intended to read in the leadsheet from a file, and then
# to keep track of the position in the lead sheet during soloing. It
# will need to provide information to other functions (such as the next
# chord) and receive information from other functions (such as a count
# indicator to move ahead)

from music import *
from Analysis import *

class LeadSheet:
   def __init__(self, filename=None, beats_per_bar=None):
      """Initialises a LeadSheet object"""
      if filename is None: filename = 'SatinDoll.txt'
      if beats_per_bar is None: beats_per_bar = 4
      self.filename = filename
      self.beats_per_bar = beats_per_bar
      self.current_bar = 0
      self.current_beat = -1 # note the current usage increments the count on the first beat
      self.current_chord_index = 0
      self.total_bars = 0
      self.ended = False
      self.root = ''
      self.quality = ''
      self.chords, self.bars = self.GetChords()
      self.root_letters, self.root_letters_flat, self.root_pitches, self.root_durations, self.chord_qualities, self.chord_qualities_flat = self.ExtractRoots(self.bars, self.beats_per_bar)
      self.chord_degrees, self.base_notes, self.base_qualities = Analysis(self).TwoFiveOne()

   def beatCrotchet(self):
      if self.current_beat < self.beats_per_bar-1:
         self.current_beat += 1
         if self.current_beat == self.root_durations[self.current_chord_index]:
            # the count has reached the first bar division at which we expect a new chord
            self.current_chord_index += 1
            # note this assumes no bar is divided further than halves. Okay fo testing but needs to be improved.
      elif self.current_bar < self.total_bars-1:
         self.current_bar += 1
         self.current_beat = 0
         self.current_chord_index += 1
      else:
         self.ended = True
      # print "bar: "+str(self.current_bar+1)+" of "+str(self.total_bars)+", beat: "+str(self.current_beat+1)
      
   def getTotalBars(self):
      return self.total_bars
   
   def getCurrentBar(self):
      return self.current_bar
   
   def getCurrentBeat(self):
      return self.current_beat

   def getFirstChordInfo(self):
      key = self.base_notes[0]
      key_qual = self.base_qualities[0]
      chord = self.root_letters_flat[0]
      chord_qual = self.chord_qualities_flat[0]
      degrees = self.chord_degrees[0]
      return key, key_qual, chord, chord_qual, degrees

   def getCurrentChordInfo(self):
      key = self.base_notes[self.current_chord_index]
      key_qual = self.base_qualities[self.current_chord_index]
      chord = self.root_letters_flat[self.current_chord_index]
      chord_qual = self.chord_qualities_flat[self.current_chord_index]
      degrees = self.chord_degrees[self.current_chord_index]
      return key, key_qual, chord, chord_qual, degrees

   def getNextBeatChordInfo(self):
      if self.current_chord_index < len(self.base_notes)-1:
         key = self.base_notes[self.current_chord_index+1]
         key_qual = self.base_qualities[self.current_chord_index+1]
         chord = self.root_letters_flat[self.current_chord_index+1]
         chord_qual = self.chord_qualities_flat[self.current_chord_index+1]
         degrees = self.chord_degrees[self.current_chord_index+1]
      else:
         return None, None, None, None, None
      if self.current_beat < self.beats_per_bar-1:
         # it's not the last beat of the bar
         if self.current_chord_index != 0:
            # it's not the very first chord
            if self.current_beat != self.root_durations[self.current_chord_index]:
               # we're not up to a chord division
               # so there's no new chord
               return 1, 1, 1, 1, 1
      # There is a new chord written on the next beat, or it's the first chord (we've dealt with the other cases already)
      # However, the written chord could still be a repeat chord
      curKey, curKey_qual, curChord, curChord_qual, curDegrees = self.getCurrentChordInfo()
      if key == curKey and key_qual == curKey_qual and chord == curChord and chord_qual == curChord_qual:
         # it's a repeat chord
         return 1, 1, 1, 1, 1
      else:
         # it's genuinely a new chord
         return key, key_qual, chord, chord_qual, degrees

   def getChordOfBar(self, bar_number=None):
      if bar_number is None: bar_number = 0
      return self.root_letters[bar_number], self.chord_qualities[bar_number]
   
   def getCurrentBarChords(self):
      return self.root_letters[self.current_bar], self.chord_qualities[self.current_bar]
   
   def getNextBarChords(self):
      if self.current_bar < len(self.root_letters)-1:
         return self.root_letters[self.current_bar+1], self.chord_qualities[self.current_bar+1]
      else:
         return self.root_letters[self.current_bar], self.chord_qualities[self.current_bar]
   
   def GetChords(self):
      with open(self.filename) as f:
         chords_rough = f.readlines()
         # now chords_rough is a list where each list element
         # is a line (as a string) from the file
         
      chords = [] # create an empty list for the chords
         
      for line in chords_rough:
         if line[0] == '%' or line[0] == '#': # first character is '%' or '#'
            pass # it's a comment line; skip it
         elif line == []:
            pass # it's an empty line; skip it
         else:
            line = line.split() # break down using whitespace as delimiter
            for element in line: # now take each element in the 'line' list
               chords.append(element) # and append it to the 'chords' list
               
      # Now we have a list of all the chords and bar separators.
      # We want to group these back into bars
      # Note - we could have done this on the first pass, but there would
      # have been no way for a bar to carry over a newline
      
      bars = []
      this_bar = []
      for element in chords: # each element is a single chord or a barline
         if element == '|': # end of a bar
            bars.append(this_bar) # add existing bar to the list of bars
            self.total_bars += 1 # add one to the total bar count
            this_bar = [] # start a fresh new bar
         else:
            this_bar.append(element) # add the chord to the current bar
      return(chords, bars)
   
   def BreakDown(self, bar, beats):
      roots = []
      durations = []
      qualities = []
      chord_duration = beats/len(bar) # because the mini-language requires bars to be evenly divided
      for chord in bar:
         # convert the standard chord notation into Jython notation
         # and extract the chord type
         foundquality = False
         if chord[0] == '/': # repeat the previous chord
            pass
            #root = 'R'
            #quality = 'R'
         else:
            self.root = chord[0]
            # check if it's a sharp or flat
            if len(chord) > 1:
               if chord[1] == 'b':
                  self.root += 'F'
                  # now remove the symbol to shorten the chord
                  chord = chord[0] + chord[2:] # concatenate the first character with the 2nd+ characters
               elif chord[1] == '#':
                  self.root += 'S'
                  chord = chord[0] + chord[2:]
            # now check for major/minor/dominant indications
            if len(chord) == 1:
               foundquality = True
               self.quality = 'major'
               qualpos = 0
            elif chord[1] == 'M':
               foundquality = True
               self.quality = 'major'
               qualpos = 1
            elif chord[1] == 'm' or chord[1] == '-':
               foundquality = True
               self.quality = 'minor'
               qualpos = 1
            elif chord[1] == '7' or chord[1] == '9':
               foundquality = True
               self.quality = 'dominant'
               qualpos = 1
            
         roots.append(self.root)
         durations.append(chord_duration)
         qualities.append(self.quality)
      
      return(roots, durations, qualities)
   
   def Octavify(self, roots, octave): # octave number as string, to make concatenation easier
      MIDI_nums = []
      for element in roots:
         element += octave # concatenation of chord root with MIDI octave number
         note = eval(element) # Jython Music evaluates the string to a MIDI note number
         MIDI_nums.append(note)
      return(MIDI_nums)
   
   def ExtractRoots(self, bars, beats_per_bar):
      root_letters = []
      roots_octavified = [] # initialise an empty list for the root notes
      durations = [] # initialise an empty list for the durations
      qualities = [] # initialise an empty list for the chord qualities
      last_root = 'NC' # initialise the last root, which will be needed if there's a chord repeat symbol
      last_quality = 'NC' # ditto for quality
      # Work through one bar at a time
      for bar_count, bar in enumerate(bars):
         # get the root notes and durations
         roots_this_bar, durations_this_bar, qualities_this_bar = self.BreakDown(bar, beats_per_bar)
         root_letters.append(roots_this_bar)
         if roots_this_bar[-1] != 'R': # the bar contains actual chords, not a 'repeat chord' symbol
            root_numbers = self.Octavify(roots_this_bar, '3') # pass the MIDI octave number as a string
            last_root = root_numbers
            last_quality = qualities_this_bar
         else:
            root_numbers = last_root
            qualities_this_bar = last_quality
         roots_octavified.append(root_numbers)
         durations.append(durations_this_bar)
         qualities.append(qualities_this_bar)
      # the next lines make 'flat' lists out of the lists of lists
      # note I do not want to make the root letters list flat: I want a list item per bar, not per chord (i.e. not flat)
      roots_octavified_flat = [item for sublist in roots_octavified for item in sublist]
      durations_flat = [item for sublist in durations for item in sublist]
      qualities_flat = [item for sublist in qualities for item in sublist]
      root_letters_flat = [item for sublist in root_letters for item in sublist]
      return root_letters, root_letters_flat, roots_octavified_flat, durations_flat, qualities, qualities_flat
   
   def GetRoots(self):
      pitches, durations = self.root_pitches, self.root_durations
      return pitches, durations
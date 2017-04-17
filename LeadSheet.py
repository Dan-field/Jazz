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

class LeadSheet:
   def __init__(self, filename=None, beats_per_bar=None):
      """Initialises a LeadSheet object"""
      if filename is None: filename = 'SatinDoll.txt'
      if beats_per_bar is None: beats_per_bar = 4
      self.filename = filename
      self.beats_per_bar = beats_per_bar
      self.current_bar = 0
      self.current_beat = -1 # note the current usage increments the count on the first beat
      self.total_bars = 0
      self.chords, self.bars = self.GetChords()
      self.root_pitches, self.root_durations = self.ExtractRoots(self.bars, self.beats_per_bar)
      
   def beatCrotchet(self):
      if self.current_beat < self.beats_per_bar-1:
         self.current_beat += 1
      else:
         self.current_bar += 1
         self.current_beat = 0
#      print "bar: "+str(self.current_bar+1)+" of "+str(self.total_bars)+", beat: "+str(self.current_beat+1)
      
   def getTotalBars(self):
      return self.total_bars
   
   def getCurrentBar(self):
      return self.current_bar
   
   def getCurrentBeat(self):
      return self.current_beat
   
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
         quality = ''
         foundquality = False
         if chord[0] == '/': # repeat the previous chord
            root = 'R'
         else:
            root = chord[0]
            # check if it's a sharp or flat
            if len(chord) > 1:
               if chord[1] == 'b':
                  root += 'F'
                  # now remove the symbol to shorten the chord
                  chord = chord[0] + chord[2:] # concatenate the first character with the 2nd+ characters
               elif chord[1] == '#':
                  root += 'S'
                  chord = chord[0] + chord[2:]
            # now check for major/minor/dominant indications
            if len(chord) == 1:
               foundquality = True
               quality = 'major'
               qualpos = 0
            elif chord[1] == 'M':
               foundquality = True
               quality = 'major'
               qualpos = 1
            elif chord[1] == 'm' or chord[1] == '-':
               foundquality = True
               quality = 'minor'
               qualpos = 1
            elif chord[1] == '7' or chord[1] == '9':
               foundquality = True
               quality = 'dominant'
               qualpos = 1
            
         roots.append(root)
         durations.append(chord_duration)
         qualities.append(quality)
#         print root, quality
      
      return(roots, durations)
   
   def Octavify(self, roots, octave): # octave number as string, to make concatenation easier
      MIDI_nums = []
      for element in roots:
         element += octave # concatenation of chord root with MIDI octave number
         note = eval(element) # Jython Music evaluates the string to a MIDI note number
         MIDI_nums.append(note)
      return(MIDI_nums)
   
   def ExtractRoots(self, bars, beats_per_bar):
      roots = [] # initialise an empty list for the root notes
      durations = [] # initialise an empty list for the durations
      last_root = 'NC' # initialise the last root, which will be needed if there's a chord repeat symbol
      # Work through one bar at a time
      for bar_count, bar in enumerate(bars):
         # get the root notes and durations
         roots_this_bar, durations_this_bar = self.BreakDown(bar, beats_per_bar)
         if roots_this_bar[-1] != 'R': # the bar contains actual chords, not a 'repeat chord' symbol
            root_numbers = self.Octavify(roots_this_bar, '3') # pass the MIDI octave number as a string
            last_root = root_numbers
         else:
            root_numbers = last_root
         roots.append(root_numbers)
         durations.append(durations_this_bar)
      # the next two lines make 'flat' lists out of the lists of lists
      roots_flat = [item for sublist in roots for item in sublist]
      durations_flat = [item for sublist in durations for item in sublist]
      return roots_flat, durations_flat
   
   def GetRoots(self):
      pitches, durations = self.root_pitches, self.root_durations
      return pitches, durations
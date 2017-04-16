###############################################################
# Improfunctions by Daniel Field                              #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# functions included:
#
# GetChords(fname) - reads the chord chart
# BreakDown(bar, beats) - breaks a bar into its roots and durations (crotchet = 1.0)
# Octavify(roots, octave) - appends octave number to the root names

from music import *

def GetChords(fname):
   with open(fname) as f:
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
         this_bar = [] # start a fresh new bar
      else:
         this_bar.append(element) # add the chord to the current bar

   return(chords, bars)

def BreakDown(bar, beats):
   roots = []
   durations = []
   chord_duration = beats/len(bar) # because the mini-language requires bars to be evenly divided
   for chord in bar:
      # convert the standard chord notation into Jython notation
      # and extract the chord type
      foundquality = False
      if chord[0] == '/':
         root = 'R'
      else:
         root = chord[0]
         if len(chord) > 1:
            if chord[1] == 'b':
               root += 'F'
            elif chord[1] == '#':
               root += 'S'
            elif chord[1] == 'M':
               foundquality = True
               quality = 'major'
               qualpos = 1
            elif chord [1] == 'm' or chord [1] == '-':
               foundquality = True
               quality = 'minor'
               qualpos = 1
      roots.append(root)
      durations.append(chord_duration)
   
   return(roots, durations)

def Octavify(roots, octave): # octave number as string, to make concatenation easier
   MIDI_nums = []
   for element in roots:
      element += octave # concatenation of chord root with MIDI octave number
      note = eval(element) # Jython Music evaluates the string to a MIDI note number
      MIDI_nums.append(note)
   return(MIDI_nums)

def ExtractRoots(bars, beats_per_bar):
   roots = [] # initialise an empty list for the root notes
   durations = [] # initialise an empty list for the durations
   last_root = 'NC' # initialise the last root, which will be needed if there's a chord repeat symbol
   # Work through one bar at a time
   for bar_count, bar in enumerate(bars):
      # get the root notes and durations
      roots_this_bar, durations_this_bar = BreakDown(bar, beats_per_bar)
      if roots_this_bar[-1] != 'R': # the bar contains actual chords, not a 'repeat chord' symbol
         root_numbers = Octavify(roots_this_bar, '3') # pass the MIDI octave number as a string
         last_root = root_numbers
      else:
         root_numbers = last_root
      roots.append(root_numbers)
      durations.append(durations_this_bar)
   # the next two lines make 'flat' lists out of the lists of lists
   roots_flat = [item for sublist in roots for item in sublist]
   durations_flat = [item for sublist in durations for item in sublist]
   return roots_flat, durations_flat
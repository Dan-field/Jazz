from music import *
from random import *

# --- INPUT ---
# This is the same as in version 0.01
# Note there's currently very little flexibility in the input file structure

# open the file and read the lines as one chord per line
fname = "Autumn.txt"
with open(fname) as f:
   chords = f.readlines()
# Remove the 'newline' characters from the elements
chords = [x.strip('\n') for x in chords]

# --- ANALYSIS ---
# Set up empty lists that will hold the chord note sequences
roots = []
thirds = []
fifths = []
sevenths = []
ninths = []

# Identify the chord notes of each chord and write them into the lists
for chord in chords:
   quality = ''               # reset the chord quality to be empty
   flat5 = False              # reset the flat 5th flag
   chars = len(chord)         # the chord symbol might be any length from 1 to 5+
   root = chord[0]            # the first symbol must be the root
   if chars == 1:
      quality = 'Major'       # a single-letter chord is a Major
   else:                      # second digit could be sharp/flat or a modifier
      if chord[1] == 'b':     # flat
         root+= 'F'
      elif chord[1] == 's':   # sharp
         root+= 'S'
      elif chord[1] == 'M':   # major 7th
         quality = 'Major'
      elif chord[1] == 'm' or chord[1] == '-':   # minor 7th
         quality = 'minor'
      elif chord[1] == '7':   # dominant 7th
         quality = 'dominant'
   root+= '3'                 # this is a string version of the root
   rt_val = eval(root)        # evaluate the numerical value of the root note (python music function)
   roots.append(rt_val)       # the roots are known
   
   # third digit would either be the main modifier or a subsequent modifier
   if chars == 2 and quality == '':    # would be a sharp or flat with no further symbols, i.e. Major
      quality = 'Major'
   if chars > 2 and quality == '':
      if chord[2] == 'M':
         quality = 'Major'
      elif chord[2] == 'm' or chord[2] == '-':
         quality = 'minor'
      elif chord[2] == '7':
         quality = 'dominant'
         
   # check if there's a flat 5th on a minor chord by searching for 'b5'
   if quality == 'minor' and chars > 3 and chord[2] == 'b' and chord[3] == '5' \
      or quality == 'minor' and chars > 4 and chord[3] == 'b' and chord[4] == '5' \
      or quality == 'minor' and chars > 5 and chord[4] == 'b' and chord[5] == '5':
         flat5 = True
      
   # Now we know the root and the chord quality. We can build up the chords
   if quality == 'Major':
      third = rt_val+4
      fifth = rt_val+7
      seventh = rt_val+11
      ninth = rt_val+14
   elif quality == 'minor':
      third = rt_val+3
      fifth = rt_val+7
      seventh = rt_val+10
      ninth = rt_val+14
      if flat5 == True:       # don't forget to flatten the 5th if required
         fifth = rt_val+6
         ninth = rt_val+13    # flatten the 9th of a minor flat 5
   else:                      # at this stage, anything unspecified will be treated as a dom 7th
      third = rt_val+4
      fifth = rt_val+7
      seventh = rt_val+10
      ninth = rt_val+14
      
   # put these chord notes into the chord note lists
   thirds.append(third)
   fifths.append(fifth)
   sevenths.append(seventh)
   ninths.append(ninth)
   
# End of loop: now it goes on to the next chord in the chord list

# --- ANALYSIS IS COMPLETE ---
# We now have lists containing the roots, 3rds, 5ths, 7ths and 9ths in sequence

# --- MELODY GENERATION ---
# In this version, we will:
# 1. For each A-section, randomly choose to start on the 3rd, 5th or 7th of the first chord
# 2. always move to the nearest note in the next chord
# Sticking with half-notes on beats 1 & 3 at the moment
# First set up the phrase
smallSteps = Phrase()
smallSteps.setTempo(150)

# At each step, select the closest available note
for i, R in enumerate(roots):
   if i == 0 or i == 16:   # first note of a new phrase
      # randomly select the 3rd, 5th or 7th
      note = choice([thirds[i], fifths[i], sevenths[i]])
   else:      # not used on the first note of each phrase. We want to continue after that.
      # first specify the possible notes, being the chordal notes possibly in the adjacent octaves
      possibleNotes = [thirds[i]-12, fifths[i]-12, sevenths[i]-12, thirds[i], fifths[i],
                     sevenths[i], thirds[i]+12, fifths[i]+12, sevenths[i]+12]
      # note: removed 9ths due to 'taste' issues. The 9ths will require more complexity
      # set up a list called noteDifferences, then subtract the previous note from the list
      noteDifferences = possibleNotes
      noteDifferences[:] = [n - previousNote for n in possibleNotes]
      # we now have a list showing the differences between the previous note and the possible next notes
      # identify the smallest value (can be +'ve or -'ve)
      select = min(noteDifferences, key=abs)
      note = previousNote+select
   smallSteps.addNote(note, HN)
   previousNote = note

# OUTPUT
Play.midi(smallSteps)
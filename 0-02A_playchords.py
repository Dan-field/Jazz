from music import *

# --- INPUT ---
# This is the same as in version 0.01
# Note there's currently no flexibility in the input file structure

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
   root+= '4'                 # this is a string version of the root
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

# TEST OUTPUT
# play the chords
playChords = Phrase()
playChords.setTempo(120)
for i, R in enumerate(roots):
   playChords.addChord([roots[i], thirds[i], fifths[i], sevenths[i]], QN)
   
Play.midi(playChords)
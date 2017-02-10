from music import *
from random import *
from itertools import *

# --- INPUT ---
# Note there's currently very little flexibility in the input file structure

# open the file and read the lines as one chord per line
fname = "Autumn.txt"
with open(fname) as f:
   all_chords = f.readlines()
# Remove the 'newline' characters from the elements
all_chords = [x.strip('\n') for x in all_chords]

# set up a phrase object
improv = Phrase()

# --- BREAK INTO FOUR-BAR PHRASES ---
# In this version, we will deal with the improvisation four bars at a time
# The following two lines create a loop over 8 chords at a time
for chord1, chord2, chord3, chord4, chord5, chord6, chord7, chord8 in izip(*[iter(all_chords)]*8):
   chords = [chord1, chord2, chord4, chord4, chord5, chord6, chord7, chord8]

   # --- ANALYSIS ---
   # Set up empty lists that will hold the chord note sequences
   roots = []
   thirds = []
   fifths = []
   sevenths = []
   ninths = []
   preferred_scales = []

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
         preferred_scale = 'Major'
      elif quality == 'minor':
         third = rt_val+3
         fifth = rt_val+7
         seventh = rt_val+10
         ninth = rt_val+14
         preferred_scale = 'Dorian'
         if flat5 == True:       # don't forget to flatten the 5th if required
            fifth = rt_val+6
            ninth = rt_val+13    # flatten the 9th of a minor flat 5
            preferred_scale = 'Min-b5'
      else:                      # at this stage, anything unspecified will be treated as a dom 7th
         third = rt_val+4
         fifth = rt_val+7
         seventh = rt_val+10
         ninth = rt_val+14
         preferred_scale = 'Mixolydian'
         
      # put these chord notes into the chord note lists
      thirds.append(third)
      fifths.append(fifth)
      sevenths.append(seventh)
      ninths.append(ninth)
      preferred_scales.append(preferred_scale)
      
   # End of loop: now it goes on to the next chord in the chord list
   
   # --- ANALYSIS IS COMPLETE ---
   # We now have lists containing the roots, 3rds, 5ths, 7ths and 9ths in sequence
   
   # --- MELODY GENERATION WITH RHYTHM ---
   # The steps are as follows:
   # 1. pick target chord notes to end each 2-bar section on
   # 2. pick phrase shapes for each 2-bar section
   # 3. pick a phrase melodic range; this may be determined partly by the end notes
   # 4. construct the phrase based on the parameters above, using scale notes
   
   # Pick two target notes
   # Randomly choose either the 3rd or 7th in the lower, middle or higher octave
   degree1 = choice(['third', 'seventh'])
   octave1 = choice([3, 4, 5])
   degree2 = choice(['third', 'seventh'])
   octave2 = choice([3, 4, 5])
   # Translate those selections into actual notes, using the 'third' and 'seventh' lists
   if degree1 == 'third':
      target_note1 = thirds[2]
   else: target_note1 = sevenths[2]
   # The lists are in octave 3. Add 12 or 24 for octave 4 or 5
   target_note1 = target_note1+((octave1-3)*12)
   # Now do the same for the second target note
   if degree2 == 'third':
      target_note2 = thirds[6]
   else: target_note2 = sevenths[6]
   target_note2 = target_note2+((octave2-3)*12)
   
   # Pick two phrase shapes. These are simply numbered 0 to 5 so it's an integer selection
   shape1 = randrange(6)
   shape2 = randrange(6)
   # It can be interesting to have the same shape over different chords.
   # Toss a coin to see if we'll force shape2 to match shape1
   if choice([True, False]):
      shape2 = shape1

   # Pick a target melodic range in general terms (small, medium, large)
   # This will apply to the whole four bars
   target_range = choice(['small', 'medium', 'large'])
      
# OUTPUT
# Play.midi(smallSteps)
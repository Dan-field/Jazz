from music import *
from random import *
from itertools import *
from operator import add

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
   # We now have lists containing the roots, 3rds, 5ths, 7ths, 9ths and preferred scales in sequence
   
   # --- MELODY GENERATION WITH RHYTHM ---
   # The steps are as follows:
   # 1. pick phrase shapes for each 2-bar section
   # 2. pick a phrase melodic range
   # 3. pick target chord notes to end each 2-bar section on
   # 4. construct the phrase based on the parameters above, using scale notes
   
   # (1) pick phrase shapes.
   # First build lists representing the possibile starting shapes
   shape0 = [-7, -6, -5, -4, -3, -2, -1, 0]
   shape1 = [7, 6, 5, 4, 3, 2, 1, 0]
   shape2 = [-2, 0, 2, 4, 6, 4, 2, 0]
   shape3 = [2, 0, -2, -4, -6, -4, -2, 0]
   shape4 = [2, 4, 6, 4, 2, 0, -2, 0]
   shape5 = [-2, -4, -6, -4, -2, 0, 2, 0]
   # now choose a shape for the first two bars
   target_shape1 = choice([shape0, shape1, shape2, shape3, shape4, shape5])
   # It can be interesting to have the same shape over different chords.
   # Toss a coin to see if we'll force shape2 to match shape1
   if choice([True, False]):
      target_shape2 = target_shape1
   # if not, then we'll need to choose a target_shape2 as well (noting that it's not
   # excluded from matching shape1)
   else: target_shape2 = choice([shape0, shape1, shape2, shape3, shape4, shape5])

   # (2) pick a target melodic range in general terms (small, medium, large)
   # This will apply to the whole four bars
   target_range = choice(['small', 'medium', 'large'])
   # compress or expand the target shape correspondingly
   if target_range == 'small':
      target_shape1 = [int(x*0.5) for x in target_shape1] # note some shapes end up with repeated notes
      target_shape2 = [int(x*0.5) for x in target_shape2] # but that's not considered a problem
   elif target_range == 'large':
      target_shape1 = [int(x*2) for x in target_shape1]
      target_shape2 = [int(x*2) for x in target_shape2]
    
   # (3) pick target chord notes
   # Randomly choose either the 3rd or 7th to end the first 2 bars on
   degree1 = choice(['third', 'seventh'])
   # choose an octave for the target note; 3 or 4 if the range isn't too big
   if target_range == 'small':
      octave1 = choice([3, 4])
   else:               # range might be too big; constrain it to octave 4
      octave1 = 4
   degree2 = choice(['root', 'fifth'])    # end the fourth bar on 1 or 5
   octave2 = octave1                      # avoid too much jumping around
   # Translate those selections into actual notes, using the lists
   if degree1 == 'third':
      target_note1 = thirds[2]
   else: target_note1 = sevenths[2]
   # The lists are in octave 3. Add 12 or 24 for octave 4 or 5
   target_note1 = target_note1+((octave1-3)*12)
   # Now do the same for the second target note
   if degree2 == 'fifth':
      target_note2 = fifths[6]
   else: target_note2 = roots[6]
   target_note2 = target_note2+((octave2-3)*12)
 
    
   # --- GENERATE THE FIRST TWO BARS ---
   # generate lists of possible starting notes based on the preferred scales
   # start by defining the root and scale
   start_root = roots[0]            # this is the root note in octave 3
   start_scale = preferred_scales[0]
   if start_scale == 'Major':
      start_scale = MAJOR_SCALE     # using the Jython Music built-in scale definitions
   elif start_scale == 'Dorian':
      start_scale = DORIAN_SCALE
   elif start_scale == 'Min-b5':
      start_scale = [0, 2, 3, 5, 6, 9, 10]
   elif start_scale == 'Mixolydian':
      start_scale = MIXOLYDIAN_SCALE
   else:
      start_scale = CHROMATIC_SCALE  # this is the fall-through
   # now create a list of all starting scale notes across several octaves
   scale_constructor = [start_root-36]*len(start_scale) + [start_root-24]*len(start_scale) \
                     + [start_root-12]*len(start_scale) + [start_root]*len(start_scale) \
                     + [start_root+12]*len(start_scale) + [start_root+24]*len(start_scale) \
                     + [start_root+36]*len(start_scale)
   start_scale = map(add, scale_constructor, start_scale*7)
   # we have a list of all scale notes across 7 octaves
   # now pick the nearest scale note to the desired starting note, based on the
   # target end note and the target shape
   # first the 'approximate' note; what it would be if not constrained by scale
   approximate_start_note = target_note1 + target_shape1[0]
   # now the 'actual' note, which is the nearest scale note to the approx note
   start_note = min(start_scale, key=lambda x: abs(x-approximate_start_note))

   # Hooray! We have a start note!
   
   # Do a sanity check to ensure at least either the start or finish note is in the mid-range
   # which we'll define as Bb to Bb around middle-C (MIDI notes 58 to 70
   if start_note > 70 and target_note1 > 70:
      start_note -= 12
      target_note1 -= 12
   elif start_note < 58 and target_note1 < 58:
      start_note += 12
      target_note1 += 12
   
   # select the pickup note to be a semitone above or below the start note
   pickup_note = choice([start_note+1, start_note-1])

   # Now work through target_shape1 ASSUMING it's the same chord as the start note
   # This assumption is true for 'Autumn Leaves' but will not always be true
   middle_notes = range(6)
   for i, n in enumerate(middle_notes):
      approximate_note = target_note1 + target_shape1[i+1]
      middle_notes[i] = min(start_scale, key=lambda x: abs(x-approximate_note))
      
   # -------------------------
   # --- RHYTHM GENERATION ---
   # -------------------------
   # Select a rhythm suggested in Jamey Aebersold's red book
   rhythm_number = choice(range(6))
   if rhythm_number == 0:
      notes = [REST, pickup_note, start_note]+middle_notes+[target_note1, REST]
      rhythm = [QNT, ENT, ENT, ENT, ENT, QNT, ENT, QNT, ENT, HN, HN]
   elif rhythm_number == 1:
      notes = [REST, start_note]+middle_notes[:5]+[target_note1, REST]
      rhythm = [QNT, QN, ENT, QNT, ENT, QNT, ENT, HN, HN]
   elif rhythm_number == 2:
      notes = middle_notes[0:2]+middle_notes[1:6]
      notes.insert(0, start_note)
      notes.insert(3, middle_notes[0])
      notes.insert(4, start_note)
      notes.insert(10, target_note1)
      rhythm = [QNT, ENT, QNT, ENT, DQN, EN, QNT, ENT, QNT, ENT, HN]
   elif rhythm_number == 3 or 4 or 5:
      notes = [REST, pickup_note, start_note]+middle_notes[1:6]+[target_note1, REST]
      rhythm = [QNT, ENT, QNT, ENT, QNT, ENT, QNT, ENT, HN, HN]
   
   # We have our notes, and the rythm is pre-set in this version. We're ready to build the phrase
   improv.addNoteList(notes, rhythm)


   # --- NOW REPEAT FOR THE NEXT TWO BARS ---
   # the process is essentially a repeat of the above
   start_root = roots[4]
   start_scale = preferred_scales[4]
   if start_scale == 'Major':
      start_scale = MAJOR_SCALE
   elif start_scale == 'Dorian':
      start_scale = DORIAN_SCALE
   elif start_scale == 'Min-b5':
      start_scale = [0, 2, 3, 5, 6, 9, 10]
   elif start_scale == 'Mixolydian':
      start_scale = MIXOLYDIAN_SCALE
   else:
      start_scale = CHROMATIC_SCALE  # this is the fall-through
   # now create a list of all starting scale notes across several octaves
   scale_constructor = [start_root-36]*len(start_scale) + [start_root-24]*len(start_scale) \
                     + [start_root-12]*len(start_scale) + [start_root]*len(start_scale) \
                     + [start_root+12]*len(start_scale) + [start_root+24]*len(start_scale) \
                     + [start_root+36]*len(start_scale)
   start_scale = map(add, scale_constructor, start_scale*7)
   # we have a list of all scale notes across 7 octaves
   # now pick the nearest scale note to the desired starting note, based on the
   # target end note and the target shape
   approximate_start_note = target_note2 + target_shape2[0]
   start_note = min(start_scale, key=lambda x: abs(x-approximate_start_note))

   # Hooray! We have a start note!
   
   # Do a sanity check to ensure at least either the start or finish note is in the mid-range
   # which we'll define as Bb to Bb around middle-C (MIDI notes 58 to 70
   if start_note > 70 and target_note2 > 70:
      start_note -= 12
      target_note2 -= 12
   elif start_note < 58 and target_note2 < 58:
      start_note += 12
      target_note2 += 12
   
   # select the pickup note to be a semitone above or below the start note
   pickup_note = choice([start_note+1, start_note-1])
   
   # Now work through target_shape2 ASSUMING it's the same chord as the start note
   # i.e. one chord carries through the whole first bar
   # This assumption is true for 'Autumn Leaves' but will not always be true
   middle_notes = range(6)
   for i, n in enumerate(middle_notes):
      approximate_note = target_note2 + target_shape2[i+1]
      middle_notes[i] = min(start_scale, key=lambda x: abs(x-approximate_note))
      
   # -------------------------
   # --- RHYTHM GENERATION ---
   # -------------------------
   # Select a rhythm suggested in Jamey Aebersold's red book
   # set to make the last one most likely
   rhythm_number = choice(range(6))
   if rhythm_number == 0:
      notes = [REST, pickup_note, start_note]+middle_notes+[target_note2, REST]
      rhythm = [QNT, ENT, ENT, ENT, ENT, QNT, ENT, QNT, ENT, HN, HN]
   elif rhythm_number == 1:
      notes = [REST, start_note]+middle_notes[:5]+[target_note2, REST]
      rhythm = [QNT, QN, ENT, QNT, ENT, QNT, ENT, HN, HN]
   elif rhythm_number == 2:
      notes = middle_notes[0:2]+middle_notes[1:6]
      notes.insert(0, start_note)
      notes.insert(3, middle_notes[0])
      notes.insert(4, start_note)
      notes.insert(10, target_note2)
      rhythm = [QNT, ENT, QNT, ENT, DQN, EN, QNT, ENT, QNT, ENT, HN]
   elif rhythm_number == 3 or 4 or 5:
      notes = [REST, pickup_note, start_note]+middle_notes[1:6]+[target_note2, REST]
      rhythm = [QNT, ENT, QNT, ENT, QNT, ENT, QNT, ENT, HN, HN]
   
   # We have our notes, and the rythm is pre-set in this version. We're ready to build the phrase
   improv.addNoteList(notes, rhythm)


      
# OUTPUT
#improv.setTempo(140)
#Play.midi(improv)
Write.midi(improv, 'improv1.mid')
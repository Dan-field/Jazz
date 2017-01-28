from music import *

# STEP 1: read the chords from a text file into a list
# For info: the text file must contain one chord per line,
# the note letters must be in upper case, and they will be
# interpreted as one chord every 2 beats. To hold a chord for longer
# it must be entered more than once. There's no way to have 
# shorter chords in this shakedown version (will be added later)

# open the file and read the lines into the list called "content"
# note each line of the text file becomes a separate list element
fname = "Autumn.txt"
with open(fname) as f:
   chords = f.readlines()
   
# Remove the 'newline' characters from the elements
chords = [x.strip('\n') for x in chords]

# Set up an empty list that will hold the roots
roots = []

# STEP 2: identify the root note of each chord (this is really parsing the
# input file into Jython Music standard. If the second character is 'b' (for
# 'flat') then a capital 'F' needs to be appended.
for chord in chords:
   root = chord[0]
   if chord[1] == 'b':
      root+= 'F'
   elif chord[1] == 's':
      root+= 'S'
   root+= '4'
   roots.append(root)
   
# we now have a list called 'roots' that contains all of the root notes
# in sequence

# STEP 3: for this shakedown, we just want to play the root note on beats 1
# and 3 of each bar. We need to create a phrase containing the appropriate
# notes

phr = Phrase()
for n in roots:
   n_val = eval(n)         # this is necessary because 'n' is a string,
                           # and will not be accepted as an argument
   note = Note(n_val, HN)
   phr.addNote(note)

# Now we can play it. It's wrapped in a score to allow tempo manipulation
part = Part(phr)
score = Score(150)
score.addPart(part)

Play.midi(score)
###############################################################
# Note Picker class by Daniel Field                           #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# This class maps an 'intended' note to a specific note depending
# on input parameters.
# Range is NOT considered in this class.

# Note: the assumed MIDI range is from 0 to 127

# There is an intent for this function to follow a 'functional programming'
# principle by passing all required values (no/minimal global variables).

#--------------------------------------------
#       Guide to tone classification
#--------------------------------------------
# 1. C = chord tone
# 2. G = guide tone
# 3. L = color tone
# 4. A = approach tone
# 5. S = scale tone
# 6. O = outside note
# 7. X = arbitrary tone
# 8. V = avoid tone
# 9. R = rest
#--------------------------------------------
# Note: these are partly borrowed from 
# Robert M. Keller and David R. Morrison
#--------------------------------------------


class NotePicker:
   def __init__(self):
      """Initialises an Note Picker object"""
      # any initialisation variables go here

   def pickNote(self, intended_MIDI, intended_tone, chord_notes, scale_notes=None, guide_tones=None, color_tones=None, avoid_notes=None):
      if intended_tone == 7 or intended_tone == "X": # arbitrary tone; no change required, just return the intended MIDI note
         return intended_MIDI
      if intended_tone == 9 or intended_tone == "R": # rest - no note selection required; just return a rest
         return "REST"
      # the tone is neither X nor R, therefore we need to quantise it to the desired tone type
      note_pool = chord_notes # set up a default condition of using a chord tone
      if intended_tone == 1 or intended_tone == "C": # chord tone
         pass # this is the default condition
      elif intended_tone == 2 or intended_tone == "G": # guide tone
         if guide_tones != None:
            note_pool = guide_tones
         else:
            print "No guide tones supplied. Using chord tones instead."
      elif intended_tone == 3 or intended_tone == "L": # color tone
         if color_tones != None:
            note_pool = color_tones
         else:
            print "No colour tones supplied. Using non-chord tones instead."
            note_pool = self.generateNonChordals(chord_notes)
      elif intended_tone == 4 or intended_tone == "A": # approach tone
         note_pool = self.generateApproaches(chord_notes)
      elif intended_tone == 5 or intended_tone == "S": # scale tone
         if scale_tones != None:
            note_pool = scale_tones
         else:
            print "No scale tones supplied. Using chord tones instead."
      elif intended_tone == 6 or intended_tone == "O": # outside note
         note_pool = self.generateNonChordals(chord_notes)
      elif intended_tone == 8 or intended_tone == "V": # avoid tone
         if avoid_notes != None:
            note_pool = avoid_notes
         else:
            print "No avoid tones supplied. Using non-chord tones instead."
            note_pool = self.generateNonChordals(chord_notes)
      # now we have our pool of notes to select from,
      # find the nearest pool note to the intended MIDI note
      loose_target = float(intended_MIDI)
      differences = [abs(loose_target - float(note)) for note in note_pool]
      closest = differences.index(min(differences))
      return note_pool[closest]

   def generateApproaches(self, chord_notes):
      # create a list of all notes a semitone above or below a chord note
      chromatic_notes = [element for element in range(0, 128) if element+1 in chord_notes or element-1 in chord_notes]
      approach_notes = [element for element in chromatic_notes if element not in chord_notes]
      if len(approach_notes) == 0: # would probably only happen if every note is a chord note
         print "No non-chord approach notes! Using chord notes instead."
         return chord_notes
      else:
         return approach_notes

   def generateNonChordals(self, chord_notes):
      # create a list of all non-chord notes
      nonchord_notes = [element for element in range(0, 128) if element not in chord_notes]
      if len(nonchord_notes) == 0: # would probably only happen if every note is a chord note
         print "No non-chord notes! Using chord notes instead."
         return chord_notes
      else:
         return nonchord_notes

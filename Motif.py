###############################################################
# Motif class by Daniel Field                                 #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# This class generates and develops motival shapes.

# Note: the assumed MIDI range is from 0 to 127

# There is an intent for this function to follow a 'functional programming'
# principle by passing all required values (no/minimal global variables).

from random import *

class Motif:
   def __init__(self):
      """Initialises a Motif object"""
      # any initialisation variables go here

   def generateNew(self, number_of_notes, range_in_semitones, starting_offset, shape=None):
      # shape is a number 1-6 as follows:
      # 1 = rising
      # 2 = falling (inverse of #1)
      # 3 = rising then falling back
      # 4 = inverse of #3
      # 5 = rising then falling back half way
      # 6 = inverse of #5
      if shape is None:
         shape = randint(1, 6)
      empty_motif = range(number_of_notes)
      motif = range(number_of_notes)
      average_step = float(range_in_semitones)/float(number_of_notes-1)
      if shape == 1 or shape == 2: # a linear motif
         for element in empty_motif:
            motif[element] = int(element*average_step)
      elif shape == 3 or shape == 4: # V-shaped or inverted-V-shaped
         average_step = 2.0*average_step
         for element in empty_motif:
            if float(element) <= float(number_of_notes)/2.0:
               motif[element] = min(range_in_semitones, int(element*average_step))
            else:
               motif[element] = int(range_in_semitones - average_step*(element-number_of_notes/2))
      elif shape == 5 or shape == 6: # V-shaped or inverted-V-shaped with half return
         average_step = 2.0*average_step
         for element in empty_motif:
            if float(element) <= float(number_of_notes)/2.0:
               motif[element] = min(range_in_semitones, int(element*average_step))
            else:
               motif[element] = int(range_in_semitones - 0.5*average_step*(element-number_of_notes/2))
      if shape == 2 or shape == 4 or shape == 6: # we require the negative
         neg_motif = [-a for a in motif]
         motif = neg_motif
      shifted_motif = [a+starting_offset for a in motif]
      motif = shifted_motif
      return motif

   def invert(self, motif):
      # negates values
      inverted_motif = [-a for a in motif]
      return inverted_motif

   def retrograde(self, motif):
      # reverses the order
      retrograde_motif = motif[::-1]
      return retrograde_motif

   def jitter(self, motif, strength):
      # randomly adjusts all values with a probability based on 'strength'
      # Note: strength is a float of at least 1.0.
      # Any 'strength' value less than 1.0 will have no effect.
      jitter_motif = [int(float(a)+0.5+float(strength)*(random()-0.5)) for a in motif]
      return jitter_motif

   def extendUp(self, motif, upstep):
      # adds two notes; a slight step down followed by a step up
      # if 'upstep' is negative then it works inverted
      extended_motif = [a for a in motif]
      last_note = motif[len(motif)-1]
      if upstep < 0:
         extended_motif.append(last_note + choice(range(abs(upstep))))
      else:
         extended_motif.append(last_note - choice(range(upstep)))
      extended_motif.append(last_note + upstep)
      return extended_motif

   def generateRhythms(self, number_of_notes): # initially, only three rhythms available (3 notes over 2 beats)
      weights = [1.0, 1.0, 0.5]
      choice = self.weighted_choice(weights)
      if choice == 0:
         return [4, 2, 2]
      elif choice == 1:
         return [2, 2, 4]
      elif choice == 2:
         return [2, 4, 2]

   def weighted_choice(self, weights):
      # thanks to Eli Benderski's Website
      totals = []
      running_total = 0

      for w in weights:
         running_total += w
         totals.append(running_total)
      rnd = random() * running_total
      for i, total in enumerate(totals):
         if rnd < total:
            return i



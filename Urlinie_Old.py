from MIDIInput import *
from time import sleep
from random import *


class Urlinie_Old:
   def __init__(self):

      self.weight_1 = 0
      self.weight_3 = 0
      self.weight_5 = 0
      self.weight_other = 0

      self.weight_length = 3

      self.slope = 10.0
      self.variance = 0.0

      self.loose_target_note = 64 # MIDI number

      self.timeSpacing = 4
      self.timeVariability = 0

      self.weight_beat1 = 95
      self.weight_otherDownbeat = 0
      self.weight_offBeat = 0

      self.MI = None # placeholder for MIDI Input reference
      self.LS = None # placeholder for Lead Sheet reference
      self.NS = None # placeholder for NoteSender reference

      self.current_urlinie = []

   def setMIDIInputReference(self, reference):
      self.MI = reference

   def setLeadSheetReference(self, reference):
      self.LS = reference

   def setNoteSenderReference(self, reference):
      self.NS = reference

   def newBar(self, barNo):
      self.NS.updateBar(barNo)
      if len(self.current_urlinie) > 0: # there is at least one note left in the current Urlinie
         self.NS.sendTempo(self.MI.getTempo())
         #self.NS.sendNoteEvent(self.current_urlinie.pop(0)) # remove the first list element and send it as a MIDI number
         self.NS.noteOn(self.current_urlinie.pop(0), self.LS.getTickCount()) # remove the first list element and send it as a MIDI number
      if len(self.current_urlinie) == 0:
         self.current_urlinie = self.newUrlinieWithDegreeTarget(0)

   def lastNoteFromScale(self, scale): # scale must be an ordered list of MIDI notes; first, third and fifth notes will be assumed important
      targetType = self.getLastNote()
      pitch_target = 0
      if len(scale) >= 5:
         if targetType in [1, 3, 5]:
            pitch_target = scale[targetType-1] # return scale index 0, 2 or 4 respectively
         else:
            del scale[4] # remove the fifth
            del scale[2] # remove the third
            del scale[0] # remove the root
            pitch_target = choice(scale) # now choose from the remaining notes
      return pitch_target

   def newUrlinieWithDegreeTargetAndTiming(self, pitch_target, beats_to_target, beats_per_bar, bar_beat_of_target, root_of_target, type_of_target): # pitch target should be a MIDI number (can be in any octave)
      note_list = []
      bars_to_next_I = 0
      beat_of_next_I = 0
      root_of_next_I = -1
      type_of_next_I = ""
      pitch_target = 0
      reference_scale = []
      if self.LS is not None:
         bars_to_next_I, beat_of_next_I = self.LS.BeatsToNextI()
         root_of_next_I, type_of_next_I = self.LS.RootAndTypeOfNextI()
      if root_of_next_I != -1: # we DO have an upcoming I in the lead sheet
         reference_scale = self.LS.getScale(self.LS.selectScale(root_of_next_I, type_of_next_I, root_of_next_I, type_of_next_I)) # this returns pitch interval series of I scale
         target_type = self.getLastNote() # returns 1, 3, 5 or 0 (0 means "anything else")
         print "target type = "+str(target_type)
         print "scale = "+str(reference_scale)+", root = "+str(root_of_next_I)
         if target_type == 1:
            pitch_target = reference_scale[0]+root_of_next_I # first scale degree, shifted to align with the root
         elif target_type == 3:
            pitch_target = reference_scale[2]+root_of_next_I
         elif target_type == 5:
            pitch_target = reference_scale[4]+root_of_next_I
         elif target_type == 0:
            stripped_reference_scale = [] # create a new reference scale, stripped of the 1st, 3rd and 5th elements
            for n, note in enumerate(reference_scale):
               if n not in [0, 2, 4]:
                  stripped_reference_scale.append(note)
            pitch_target = choice(stripped_reference_scale)+root_of_next_I
         else:
            pitch_target = choice(reference_scale)+root_of_next_I
         print "pitch target = "+str(pitch_target)
      notepool = self.allOctaves(pitch_target) # sets out the same pitch class across all octaves
      target = self.pickClosest(notepool, self.getLooseTargetNote())
      length = self.getLength()
      if bars_to_next_I != 0:
         length = bars_to_next_I+1 # temporary arrangement for testing arrival on the I - this overrides the length selection
      else:
         length = 0
      if length > 0:
         last_note = target
         variance = self.getVariance()
      if length > 1:
         slope_per_slot = self.getSlope()/(length-1)
         for slot in range(length):
            this_note = last_note+(length-1-slot)*slope_per_slot
            variation = (random()-0.5)*variance
            note_list.append(this_note+variation)
      elif length == 1:
         variation = (random()-0.5)*variance
         note_list.append(last_note+variation)
      print "beat affinity would be: "+str(self.getBeatType())
      print "UL Generated Note List "+str(note_list)
      return note_list

   def newUrlinieWithDegreeTarget(self, pitch_target): # pitch target should be a MIDI number (can be in any octave)
      note_list = []
      bars_to_next_I = 0
      beat_of_next_I = 0
      root_of_next_I = -1
      type_of_next_I = ""
      pitch_target = 0
      reference_scale = []
      if self.LS is not None:
         bars_to_next_I, beat_of_next_I = self.LS.BeatsToNextI()
         root_of_next_I, type_of_next_I = self.LS.RootAndTypeOfNextI()
      if root_of_next_I != -1: # we DO have an upcoming I in the lead sheet
         reference_scale = self.LS.getScale(self.LS.selectScale(root_of_next_I, type_of_next_I, root_of_next_I, type_of_next_I)) # this returns pitch interval series of I scale
         target_type = self.getLastNote() # returns 1, 3, 5 or 0 (0 means "anything else")
         print "target type = "+str(target_type)
         print "scale = "+str(reference_scale)+", root = "+str(root_of_next_I)
         if target_type == 1:
            pitch_target = reference_scale[0]+root_of_next_I # first scale degree, shifted to align with the root
         elif target_type == 3:
            pitch_target = reference_scale[2]+root_of_next_I
         elif target_type == 5:
            pitch_target = reference_scale[4]+root_of_next_I
         elif target_type == 0:
            stripped_reference_scale = [] # create a new reference scale, stripped of the 1st, 3rd and 5th elements
            for n, note in enumerate(reference_scale):
               if n not in [0, 2, 4]:
                  stripped_reference_scale.append(note)
            pitch_target = choice(stripped_reference_scale)+root_of_next_I
         else:
            pitch_target = choice(reference_scale)+root_of_next_I
         print "pitch target = "+str(pitch_target)
      notepool = self.allOctaves(pitch_target) # sets out the same pitch class across all octaves
      target = self.pickClosest(notepool, self.getLooseTargetNote())
      length = self.getLength()
      if bars_to_next_I != 0:
         length = bars_to_next_I+1 # temporary arrangement for testing arrival on the I - this overrides the length selection
      else:
         length = 0
      if length > 0:
         last_note = target
         variance = self.getVariance()
      if length > 1:
         slope_per_slot = self.getSlope()/(length-1)
         for slot in range(length):
            this_note = last_note+(length-1-slot)*slope_per_slot
            variation = (random()-0.5)*variance
            note_list.append(this_note+variation)
      elif length == 1:
         variation = (random()-0.5)*variance
         note_list.append(last_note+variation)
      print "beat affinity would be: "+str(self.getBeatType())
      print "UL Generated Note List "+str(note_list)
      return note_list

   def newUrlinie(self):
      length = self.getLength()
      note_list = []
      if length > 0:
         last_note = self.getLooseTargetNote()
         variance = self.getVariance()
      if length > 1:
         slope_per_slot = self.getSlope()/(length-1)
         for slot in range(length):
            this_note = last_note+(length-1-slot)*slope_per_slot
            variation = (random()-0.5)*variance
            note_list.append(this_note+variation)
      elif length == 1:
         variation = (random()-0.5)*variance
         note_list.append(last_note+variation)
      return note_list

   def adjustLastNoteWeights(self, slider_value):
      # assume slider_value is an integer 0-127
      # set weight 1:
      if slider_value <= 95:
         self.weight_1 = 95 - slider_value
      else:
         self.weight_1 = 0
      # set weights 3 and 5:
      if slider_value > 31:
         self.weight_3 = 64 - (slider_value/2)
      else:
         self.weight_3 = 3*slider_value/2
      self.weight_5 = self.weight_3
      # set weight other:
      if slider_value >= 32:
         self.weight_other = slider_value - 32
      else:
         self.weight_other = 0
         
   def getLastNote(self):
      choice_index = self.weighted_choice([self.weight_1, self.weight_3, self.weight_5, self.weight_other])
      if choice_index is None:
         choice_index = 0
      #print str(choice_index)
      return [1, 3, 5, 0][choice_index]

   def setLooseTargetNote(self, value):
      self.loose_target_note = value
      
   def getLooseTargetNote(self):
      return self.loose_target_note

   def adjustUrlinieLengthWeight(self, value):
      # assume value is an integer 0-127
      # we want length to be in the range 0 to 12 in proportion
      self.weight_length = int(value/10)

   def getLength(self):
      return self.weight_length

   def adjustUrlinieSlope(self, value):
      # 0-127 corresponds to the range -31.5 to +32.0
      self.slope = float(value*0.5-31.5)

   def getSlope(self):
      return self.slope

   def adjustUrlinieVariance(self, value):
      # 0-127 corresponds to the range 0.0 to +63.5
      self.variance = value*0.5

   def getVariance(self):
      return self.variance

   def adjustBeatAffinity(self, value): # use a weighting system similar to last note
      # set weight of falling on beat 1:
      if value <= 95:
         self.weight_beat1 = 95 - value
      else:
         self.weight_beat1 = 0
      # set weight of falling on another downbeat:
      if value > 31:
         self.weight_otherDownbeat = 95 - (4*value)/3
      else:
         self.weight_otherDownbeat = int(2.3*float(value))
      # set weight of falling an an offbeat:
      if value >= 32:
         self.weight_offBeat = value - 32
      else:
         self.weight_offBeat = 0

   def getBeatType(self):
      choice_index = self.weighted_choice([self.weight_beat1, self.weight_otherDownbeat, self.weight_offBeat])
      if choice_index is None:
         choice_index = 0
      #print str(choice_index)
      return [1, 3, 0][choice_index] # 1=first beat, 3=other downbeat, 0=offbeat

   def adjustTimeSpacing(self, value):
      # 0-127 input range giving spacings from 1 to 32 beats
      self.timeSpacing = int(value/4)+1

   def adjustTimeVariability(self, value):
      # 0-127 input range giving variabilities from 0 to 7
      self.timeVariability = int(value/16)

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

   def allOctaves(self, MidiNo): # Takes a single MIDI number input and returns a list of that note in all octaves
      octaves = [element*12 for element in range(11)] # produce list [0, 12, 24 ... 120]
      pc = int(MidiNo)%12 # pitch class
      result = []
      for octave in octaves:
         result.append(octave+pc) # this is the pitch class number plus the octave number
      return result

   def pickClosest(self, notepool, target): # returns the nearest note in the notepool to the target
      # check how far the potential notes are from the target
      differences = [abs(target - float(note)) for note in notepool]
      # find the closest
      closest = differences.index(min(differences))
      return notepool[closest]

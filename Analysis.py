###############################################################
# Analysis class by Daniel Field                              #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# This class is intended to conduct a jazz analysis of the chords
# in a lead sheet to identify chord functions and key centres

from music import *

class Analysis:
   def __init__(self, leadsheet=None, declared_key=None):
      """Initialises an Analysis object"""
      if leadsheet is None:
         print "caution: initialising Analysis class without a lead sheet"
      if declared_key is None:
         declared_key = 'C'
      self.leadsheet = leadsheet
      self.declared_key = declared_key
      self.chords = leadsheet.chords
      self.bars = leadsheet.bars
      self.root_letters = leadsheet.root_letters_flat
      self.root_durations = leadsheet.root_durations
      self.chord_qualities = leadsheet.chord_qualities_flat
      self.root_nums = self.RootsToNums()
      self.chord_degrees = [1] * len(self.root_letters)
      self.modes = [None] * len(self.root_letters)
      self.base_notes = [self.root_letters[-1]] * len(self.root_letters)
      self.base_qualities = ['major'] * len(self.root_letters)
      
   def RootsToNums(self):
   # The point of this function is to convert the note names into integer numbers,
   # which will allow interval relationships to be calculated numerically.
   # The note 'A' is designated as number 1, with numbers increasing by 1 per semitone.
   # If the note nams is not recognised then it gets the number 99.
      root_nums = []
      for letter in self.root_letters:
         if letter == 'A': root_nums.append(1)
         elif letter == 'AS' or letter == 'BF': root_nums.append(2)
         elif letter == 'B': root_nums.append(3)
         elif letter == 'C': root_nums.append(4)
         elif letter == 'CS' or letter == 'DF': root_nums.append(5)
         elif letter == 'D': root_nums.append(6)
         elif letter == 'DS' or letter == 'EF': root_nums.append(7)
         elif letter == 'E': root_nums.append(8)
         elif letter == 'F': root_nums.append(9)
         elif letter == 'FS' or letter == 'GF': root_nums.append(10)
         elif letter == 'G': root_nums.append(11)
         elif letter == 'GS' or letter == 'AF': root_nums.append(12)
         else: root_nums.append(99)
      return root_nums
         
      
   def TwoFiveOne(self):
   # go through the chord list looking for ii-V-I patterns
   # note: starting at the end and looking for the I, looking back
      index = len(self.root_letters)-1
      while index > 0:
         # reset the flags
         jump_val = 1
         ending_on = []
         ending_quality = []
         # could this be a V-I?
         # note: +5 or -7 semitones from the V to the I
         interval = self.root_nums[index] - self.root_nums[index-1]
         if interval in [-7, 5]:
            ending_on = self.root_letters[index]
            ending_quality = self.chord_qualities[index]
            self.chord_degrees[index] = 1
            self.chord_degrees[index-1] = 5
            # it is a V-I, but is it a ii-V-I?
            # note: +5 or -7 semitones from the ii to the V
            jump_val = 2
            interval = self.root_nums[index-1] - self.root_nums[index-2]
            if interval in [-7, 5]:
               self.chord_degrees[index-2] = 2
               # it is a ii-V-I but is it a vi-ii-V-I?
               # note +5 or -7 semitones from the vi to the ii
               jump_val = 3
               interval = self.root_nums[index-2] - self.root_nums[index-3]
               if interval in [-7, 5] or (interval in [-6, 6] and ending_quality == "minor"):
                  self.chord_degrees[index-3] = 6
                  # it is a vi-ii-V-I but is it a iii-vi-ii-V-I?
                  # note +5 or -7 semitones from the iii to the vi
                  jump_val = 4
                  interval = self.root_nums[index-3] - self.root_nums[index-4]
                  if interval in [-7, 5]:
                     self.chord_degrees[index-4] = 3
                     # could it be a vii-iii-vi-ii-V-I?
                     # note +5 or -7 semitones from the vii to the iii
                     jump_val = 5
                     interval = self.root_nums[index-4] - self.root_nums[index-5]
                     if interval in [-7, 5]:
                        self.chord_degrees[index-5] = 7
                        # could it be a iv-vii-iii-vi-ii-V-I?
                        # note +6 or -6 semitones from the vi to the vii
                        jump_val = 6
                        interval = self.root_nums[index-5] - self.root_nums[index-6]
                        if interval in [-6, 6] or (interval in [-7, 5] and ending_quality == "minor"):
                           self.chord_degrees[index-6] = 4
                           jump_val = 7
                           print "iv-vii-iii-vi-ii-V-I ending on "+ending_on+" "+ending_quality+" at chord "+str(index+1)
                           for i in range(index-6, index+1):
                              self.base_notes[i] = ending_on
                              self.base_qualities[i] = ending_quality
                        else:
                           print "vii-iii-vi-ii-V-I ending on "+ending_on+" "+ending_quality+" at chord "+str(index+1)
                           for i in range(index-5, index+1):
                              self.base_notes[i] = ending_on
                              self.base_qualities[i] = ending_quality
                     else:
                        print "iii-vi-ii-V-I ending on "+ending_on+" "+ending_quality+" at chord "+str(index+1)
                        for i in range(index-4, index+1):
                           self.base_notes[i] = ending_on
                           self.base_qualities[i] = ending_quality
                  else:
                     print "vi-ii-V-I ending on "+ending_on+" "+ending_quality+" at chord "+str(index+1)
                     for i in range(index-3, index+1):
                        self.base_notes[i] = ending_on
                        self.base_qualities[i] = ending_quality
               else:
                  print "ii-V-I ending on "+ending_on+" "+ending_quality+" at chord "+str(index+1)
                  for i in range(index-2, index+1):
                     self.base_notes[i] = ending_on
                     self.base_qualities[i] = ending_quality
            else:
               print "V-I ending on "+ending_on+" "+ending_quality+" at chord "+str(index+1)
               for i in range(index-1, index):
                  self.base_notes[i] = ending_on
                  self.base_qualities[i] = ending_quality
         index = index-jump_val
      return self.chord_degrees, self.base_notes, self.base_qualities



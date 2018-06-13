###############################################################
# NotepoolHandler class by Daniel Field                       #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# This class is intended to take a notepool (e.g. from a Musebot)
# and extend it across octaves.

class NotepoolHandler:
   def __init__(self):
      """Initialises a Notepool Handler object"""

   def buildFullRange(self, pool_values, range_top=None, range_bottom=None):
      if range_top is None: range_top = 120
      if range_bottom is None: range_bottom = 0
      full_scale = []
      pool_first_octave = []
      pool_octave = int(pool_values[0]/12)
      octaves = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108]
      for value in pool_values:
         pool_first_octave.append(value - (12*pool_octave))
      for octave in octaves:
         for value in pool_first_octave:
            if octave+value >= range_bottom and octave+value <= range_top:
               full_scale.append(octave+value)
      return full_scale

   def receiveNotepool(self, message):
      args = message.getArguments()
      new_notepool = []
      for i in range( len(args) ):
         if type(args[i]) == int:
            if args[i] > -1 and args[i] < 150:
               new_notepool.append(args[i])
      new_notepool.sort()
      return new_notepool
   
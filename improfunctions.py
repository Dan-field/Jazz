###############################################################
# Improfunctions by Daniel Field                              #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################


def GetChords(fname):
   with open(fname) as f:
      chords_rough = f.readlines()
      # now chords_rough is a list where each list element
      # is a line (as a string) from the file
      
   chords = [] # create an empty list for the chords
      
   for line in chords_rough:
      if line[0] == '%' or line[0] == '#': # first character is '%' or '#'
         pass # it's a comment line; skip it
      elif line == []:
         pass # it's an empty line; skip it
      else:
         line = line.split() # break down using whitespace as delimiter
         for element in line: # now take each element in the 'line' list
            chords.append(element) # and append it to the 'chords' list
            
   # Now we have a list of all the chords and bar separators.
   # We want to group these back into bars
   # Note - we could have done this on the first pass, but there would
   # have been no way for a bar to carry over a newline
   
   bars = []
   this_bar = []
   for element in chords:
      if element == '|':
         bars.append(this_bar)
         this_bar = []
      else:
         this_bar.append(element)

   return(chords, bars)

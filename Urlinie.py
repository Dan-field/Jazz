from MIDIInput import *
from time import sleep
from random import *
from timer import *


class Urlinie:
   def __init__(self):
      seed = range(120)
      self.contour = []
      for number in seed:
         self.contour.append(0)
      self.slope = 0
      self.semi_multiplier = 32
      self.no_of_undulations = 1
      self.undulation_gradient = 0.0
      self.arc_reference = [0, 6, 11, 17, 21, 26, 31, 35, 39, 43, 46, 50, 53, 57, 60, 63, 66, 69, 71, 74, 76, 79, 81, 83, 85, 88, 90, 91, 93, 95, 97, 98, 100, 101, 103, 104, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 115, 116, 117, 117, 118, 118, 119, 119, 119, 119, 120, 120, 120, 120, 120, 120, 120, 120, 119, 119, 119, 119, 118, 118, 117, 117, 116, 115, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 104, 103, 101, 100, 98, 97, 95, 93, 91, 90, 88, 85, 83, 81, 79, 76, 74, 71, 69, 66, 63, 60, 57, 53, 50, 46, 43, 39, 35, 31, 26, 21, 17, 11, 6, 0]
      #self.semicircle_reference = [0, 22, 31, 37, 43, 48, 52, 56, 60, 63, 66, 69, 72, 75, 77, 79, 82, 84, 86, 88, 89, 91, 93, 94, 96, 97, 99, 100, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 112, 113, 114, 114, 115, 116, 116, 117, 117, 118, 118, 118, 119, 119, 119, 119, 120, 120, 120, 120, 120, 120, 120, 120, 120, 120, 119, 119, 119, 119, 118, 118, 118, 117, 117, 116, 116, 115, 114, 114, 113, 112, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 100, 99, 97, 96, 94, 93, 91, 89, 88, 86, 84, 82, 79, 77, 75, 72, 69, 66, 63, 60, 56, 52, 48, 43, 37, 31, 22, 0]
      self.d = Display("Urlinie Contour", 240, 240, 820, 10)
      self.display_line = []
      for i, number in enumerate(self.contour):
         self.display_line.append(Point(i*2, 120-number))
      for p in self.display_line:
         self.d.add(p)
      self.MI = None # placeholder for MIDI Input reference
      self.drawingTimer = Timer(0, self.drawUL, [], False)

   def newUrlinie_firstTry(self):
      start = -self.slope
      curve = self.semi_multiplier
      newUrlinie = []
      for i, no in enumerate(self.arc_reference):
         newUrlinie.append(start*(120-i)/64 + no*curve/64)
      self.contour = newUrlinie
      self.display_line = []
      for i, number in enumerate(newUrlinie):
         self.display_line.append(Point(i*2, 120-number))
      self.d.removeAll()
      for point in self.display_line:
         self.d.add(point)

   def newUrlinie(self):
      start = -self.slope
      curve = self.semi_multiplier
      newUrlinie = []
      for i, no in enumerate(self.arc_reference):
         newUrlinie.append(start*(120-i)/64 + no*curve/64) # this gives the underlying curve without undulations
      # now add the undulations
      if self.no_of_undulations > 1:
         ref = []
         undulatedUrlinie = []
         divs = self.no_of_undulations
         grad = self.undulation_gradient
         for no in range(120):
            ref.append((120/divs)*(1+(divs*no/120))) # create a vector pointing to the end of each segment, eg [15, 15, 15, ..., 30, 30, ..., 60..., 120]
         for i in range(120):
            undulatedUrlinie.append(newUrlinie[ref[i]-1]-int(grad*(ref[i]-i))) # create line segments that finish on the underlying curve
         newUrlinie = undulatedUrlinie
      self.contour = newUrlinie
      self.drawingTimer.start()
      return newUrlinie

   def drawUL(self):
      self.display_line = []
      newUrlinie = self.contour
      for i, number in enumerate(newUrlinie):
         self.display_line.append(Point(i*2, 120-number))
      self.d.removeAll()
      for point in self.display_line:
         self.d.add(point)

   def adjustOverallSlope(self, slider_value):
      # assume slider_value is an integer 0-127
      # Change: this now adjusts OVERALL SLOPE
      self.slope = slider_value-63
         
   def adjustArcMultiplier(self, value):
      # Change: this now adjusts SEMICIRCLE MULTIPLIER
      self.semi_multiplier = value-63
      
   def adjustNumberOfUndulations(self, value):
      # Change: this now adjusts NUMBER OF UNDULATIONS
      self.no_of_undulations = (value/16)+1 # result from 1 to 8

   def adjustUndulationGradient(self, value):
      # Change: this now adjusts undulation gradient
      self.undulation_gradient = (value-63.0)/(8.0*self.no_of_undulations)

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

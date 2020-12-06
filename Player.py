###############################################################
# Player class by Daniel Field                                #
#                                                             #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# The 'Player' decides what notes to play, and when.
# It has access to information about:
# - timing / beats
# - progress through the lead sheet, including distance to end and distance to next V-I (if applicable)
# - current chord and key

from gui import *
from guicontrols import *
from midi import *
from music import *
from random import *
#from HarmonicStructure import *

class Player:
   def __init__(self):
      """Initialises a Player object"""
      # set up the class variables
      self.rangeTop = 85 # MIDI number of top note
      self.rangeBottom = 42 # MIDI number of bottom note
      self.currentUrlinie = []
      self.baseMotif = []
      self.workingMotif = []
      self.ULLength = 120 # this is the number of values in the UL vector - which is determined by the Urlinie generator
      self.ULPosition = 0 # index
      self.nextTargetNoteRelative = 0
      self.ULJump = 30
      self.ULBeatWait = 4
      self.ULBeatsToGo = 0
      self.MotifBeatsToGo = 0
      self.DBAffinity = 127
      self.IAffinity = 127
      self.swinging = False
      self.noteDensity = 63
      self.beatHeirarchy = 127
      self.heirarchyZero = 0 # extra weight given to the downbeat
      self.heirarchyOne = 0 # extra weight given to beat 3
      self.heirarchyThree = 0 # extra weight given to the off quavers
      self.scale = [0, 2, 4, 5, 7, 9, 11] # start with the Major/Ionian scale
      self.scaleBase = 0 # start with 'C'
      self.fullRangedScale = [] # holder for the current scale expressed across the current range of the Player
      self.rangedScaleOf1s = [] # holder for the current 1st degrees of the scale, across current range
      self.rangedScaleOf3s = [] # holder for the current 3rd degrees of the scale, across current range
      self.rangedScaleOf5s = [] # holder for the current 5th degrees of the scale, across current range
      self.rangedScaleOf0s = [] # holder for scale notes that are not 1st, 3rd or 5th degrees, across current range
      self.finishedUL = False
      self.weight_1 = 80 # assume slider 1 starts at value 15
      self.weight_3 = 22
      self.weight_5 = 22
      self.weight_other = 0
      self.thisTick = 0
      self.thisBar = 0
      self.ticksPerBar = 48
      self.cumulativeBars = 0
      self.motifScale = 30
      self.newULTimer = Timer(0, self.getNewUrlinie, [], False) # the idea is to put the Urlinie generator on its own thread

      # set placeholder for references to other classes
      self.UL = None # placeholder for UrLinie object
      self.NS = None # placeholder for Note Sender object
      self.LS = None # placeholder for Lead Sheet object
      self.MI = None # placeholder for MIDI Input object

   def setUrlinieReference(self, newUL):
      self.UL = newUL

   def setNoteSenderReference(self, newNS):
      self.NS = newNS
      self.NS.setReverb(0)

   def setLeadSheetReference(self, newLS):
      self.LS = newLS

   def setMIDIInputReference(self, newMI):
      self.MI = newMI

   def setSwinging(self, newSwinging):
      self.swinging = newSwinging

   def setScale(self, newScale, newScaleBase):
      self.scale = newScale
      self.scaleBase = newScaleBase
      self.buildFullScale(newScale, newScaleBase)

   def setNoteDensity(self, newDensity):
      self.noteDensity = newDensity

   def setBeatHeirarchy(self, newBeatHeirarchy):
      self.beatHeirarchy = newBeatHeirarchy
      self.heirarchyZero = newBeatHeirarchy-64
      self.heirarchyOne = (newBeatHeirarchy/2)-32
      self.heirarchyThree = (-newBeatHeirarchy/2)+32

   def getNewUrlinie(self):
      self.currentUrlinie = self.UL.newUrlinie()
      self.finishedUL = False
      self.ULPosition = 0
      if self.IAffinity > 63:
         beatsToNextI = self.LS.BeatsToNextI()
         if beatsToNextI < 1:
            beatsToNextI = 1
         newValue = 120*self.ULBeatWait/beatsToNextI
         self.MI.setValue20(int(2*(newValue-1))) # adjust the ULJump value

   def setScaleDegreeWeights(self, newValue):
      # assume slider_value is an integer 0-127
      # set weight 1 (range 0 to 95):
      if newValue <= 95:
         self.weight_1 = 95 - newValue
      else:
         self.weight_1 = 0
      # set weights 3 and 5 (range 0 to 48):
      if newValue > 31:
         self.weight_3 = 64 - (newValue/2)
      else:
         self.weight_3 = 3*newValue/2
      self.weight_5 = self.weight_3
      # set weight other (range 0 to 95):
      if newValue >= 32:
         self.weight_other = newValue - 32
      else:
         self.weight_other = 0

   def setMotifShape(self, newValue):
      workingMotif = []
      if newValue < 60:
         for n in range(60):
            if n < 59-newValue:
               workingMotif.append(n-59+newValue+newValue)
            else:
               workingMotif.append(59-n)
      elif newValue < 90:
         for n in range(60):
            if n < newValue-60:
               workingMotif.append(299-(newValue*4)+n)
            elif n < 120-newValue:
               workingMotif.append(59-n-((newValue-60)*2))
            else:
               workingMotif.append(n-59)
      elif newValue < 121:
         for n in range(60):
            if n < newValue-90:
               workingMotif.append((newValue*4)-419-n)
            elif n < 150-newValue:
               workingMotif.append(n-59+((newValue-90)*2))
            else:
               workingMotif.append(59-n)
      self.baseMotif = workingMotif
      self.scaleMotif()



   def setMotifScale(self, newValue): # newValue will range between 64 and -63. Let 30 mean a scale of 1:1 (and -30 mean -1:1)
      self.motifScale = newValue
      targetNote = self.nextTargetNoteRelative
      workingMotif = self.baseMotif
      scaledMotif = []
      for element in workingMotif:
         scaledMotif.append(int((element*newValue)/30)+targetNote)
      self.workingMotif = scaledMotif

   def setULJump(self, newValue):
      self.ULJump = (newValue/2)+1 # value from 1 to 64

   def setULBeatWait(self, newValue):
      self.ULBeatWait = (newValue/8)+1 # value from 1 to 16

   def setDownBeatAffinity(self, newValue):
      self.DBAffinity = newValue

   def setIAffinity(self, newValue):
      self.IAffinity = newValue

   def setNextTargetNote(self): # sets next upcoming target note based on Urlinie and Parameters
      # select the value from the UL vector according to the UL jump value
      if len(self.currentUrlinie) > 0:
         pos = self.ULPosition
         jump = self.ULJump
         UL = self.currentUrlinie
         if pos + jump < len(UL):
            pos += jump
         else:
            pos = len(UL)-1
            self.finishedUL = True
         rangeSize = self.rangeTop-self.rangeBottom
         nextNoteScaled = (self.rangeBottom+(rangeSize/2))+(UL[pos]*(rangeSize)/240) # scale the UL range (+/- 120) to the instrument's range
         self.nextTargetNoteRelative = nextNoteScaled
         self.scaleMotif()
         self.ULPosition = pos
         # choose the number of beats till next UL note
         setValue = self.ULBeatWait
         DBModifier = self.DBAffinity
         beatsToNextDB = self.LS.BeatsPerBar() - self.LS.CurrentBeat()
         if DBModifier > 63:
            self.ULBeatsToGo = beatsToNextDB
         else:
            self.ULBeatsToGo = setValue

   def planWayToNextTargetNote(self):
      pass

   def scaleMotif(self):
      if len(self.baseMotif) > 0:
         finishingNote = self.nextTargetNoteRelative
         motif = self.baseMotif
         newMotif = []
         for note in motif:
            newMotif.append(note+finishingNote)
         self.workingMotif = newMotif

   def getLastNote(self):
      choice_index = self.weighted_choice([self.weight_1, self.weight_3, self.weight_5, self.weight_other])
      if choice_index is None:
         choice_index = 0
      #print str(choice_index)
      return [1, 3, 5, 0][choice_index]

   def Tick(self, tick):
      #breakDown = tick%12
      #if breakDown == 0 or breakDown == 4 or breakDown == 8:
      #   self.NS.sendNoteShort(40)
      if tick == 0:
         self.thisBar += 1
      self.thisTick = tick # note 'ticks per bar' is set to 48 in the HarmonicStructure class; that's 12 ticks per crotchet
      if tick%2 == 0: # even-numbered tick, count down on the Motif list
         self.MotifBeatsToGo -= 1
         if tick%6 == 0: # it's a quaver tick
            heirarchyWeight = 0
            if tick == 0: # this is a downbeat
               heirarchyWeight = self.heirarchyZero
            elif tick == 24: # this is beat three
               heirarchyWeight = self.heirarchyOne
            elif tick%12 == 0: # this is beat 2 or 4
               heirarchyWeight = 0
            else: # this is an off quaver beat
               heirarchyWeight = self.heirarchyThree
            if self.noteDensity+heirarchyWeight > random()*126.0:
               self.playNextMotifNote(self.getLastNote())
         #if self.noteDensity > 100: # high density; play every note
         #   if tick%6 == 0: # play a quaver - could be modified later to allow higher densities, but sticking with quaver for now
         #      self.playNextMotifNote(self.getLastNote())

   def playNextMotifNote(self, scaleDegree=None):
      if len(self.workingMotif) > 0:
         notepool = []
         if scaleDegree is None:
            notepool = self.fullRangedScale
         elif scaleDegree == 1:
            notepool = self.rangedScaleOf1s
         elif scaleDegree == 3:
            notepool = self.rangedScaleOf3s
         elif scaleDegree == 5:
            notepool = self.rangedScaleOf5s
         elif scaleDegree == 0:
            notepool = self.rangedScaleOf0s
         else:
            notepool = self.fullRangedScale
         position = 60-self.MotifBeatsToGo
         while position < 1:
            position += 60 # make sure the 'position' value ends up from 0 to 59 so it can index the Motif list
         while position > 60:
            position -= 60
         target = self.workingMotif[position-1]
         #targetOctavified = self.allOctaves(target)
         #target = self.pickClosest(targetOctavified, (self.rangeTop+self.rangeBottom)/2)
         selectedNote = self.pickClosest(notepool, target)
         #self.NS.sendNoteRaw(selectedNote)
         self.NS.sendNoteRawWithTickNo(selectedNote, self.thisTick, self.thisBar, self.ticksPerBar)
      else:
         print "no motif"

   def playBassAccompaniment(self, chordBase): #chordBase is a MIDI number 0-11, chordType is min, Maj, Dom, dim or mb5
      self.NS.sendNoteBass(chordBase+36)

   def playAccompaniment(self, chordBase, chordType): #chordBase is a MIDI number 0-11, chordType is min, Maj, Dom, dim or mb5
      if chordType[0] == "m":
         self.NS.sendNoteRaw(chordBase+60+3)
         self.NS.sendNoteRaw(chordBase+60+10)
      elif chordType[0] == "D":
         self.NS.sendNoteRaw(chordBase+60+4)
         self.NS.sendNoteRaw(chordBase+60+10)
      elif chordType[0] == "M":
         self.NS.sendNoteRaw(chordBase+60+4)
         self.NS.sendNoteRaw(chordBase+60+11)
      elif chordType[0] == "d":
         self.NS.sendNoteRaw(chordBase+60+3)
         self.NS.sendNoteRaw(chordBase+60+9)

   def resetBar(self):
      self.thisBar = 0
      self.thisTick = 0

   def beat(self):
      self.ULBeatsToGo -= 1
      if self.ULBeatsToGo < 1:
         # self.playNextTargetNote(self.getLastNote()) # this plays the UL note; it tends to double up with the Motif note
         self.setNextTargetNote()
         self.MotifBeatsToGo = self.ULBeatsToGo*6 # allows subdivisions of 2 or 3, note Motif list only has 60 values so needs to loop if more than 10 beats
      if self.finishedUL:
         self.newULTimer.start()

   def playNextTargetNote(self, scaleDegree=None): # 'scaleDegree' is 1, 3, 5 or 0 to mean '1st, 3rd, 5th or any other' note of the scale
      print "playing scale degree "+str(scaleDegree)
      notepool = []
      if scaleDegree is None:
         notepool = self.fullRangedScale
      elif scaleDegree == 1:
         notepool = self.rangedScaleOf1s
      elif scaleDegree == 3:
         notepool = self.rangedScaleOf3s
      elif scaleDegree == 5:
         notepool = self.rangedScaleOf5s
      elif scaleDegree == 0:
         notepool = self.rangedScaleOf0s
      else:
         notepool = self.fullRangedScale
      target = self.nextTargetNoteRelative
      #targetOctavified = self.allOctaves(target)
      #target = self.pickClosest(targetOctavified, (self.rangeTop+self.rangeBottom)/2)
      selectedNote = self.pickClosest(notepool, target)
      #self.NS.sendNoteRaw(selectedNote)
      self.NS.sendNoteRawWithTickNo(selectedNote, self.thisTick, self.thisBar, self.ticksPerBar)

   def allOctaves(self, MidiNo): # Takes a single MIDI number input and returns a list of that note in all octaves
      octaves = [element*12 for element in range(11)] # produce list [0, 12, 24 ... 120]
      pc = int(MidiNo)%12 # pitch class
      result = []
      for octave in octaves:
         result.append(octave+pc) # this is the pitch class number plus the octave number
      return result

   def buildFullScale(self, scale_values, rootMIDI): # Takes a list of MIDI note numbers and returns the same notes spread across all octaves
      values = []
      one = []
      three = []
      five = []
      zeros = []
      full_scale = []
      all_ones = []
      all_threes = []
      all_fives = []
      all_zeros = []
      rootMIDI = rootMIDI%12 # get the pitch class of the root
      for index, value in enumerate(scale_values):
         value = int(value)%12 # get the pitch class
         if value not in values: # only append it if it's not already in the list
            values.append(value)
         if index == 0: # it's the first pitch class
            one.append(value)
         elif index == 2: # it's the third pitch class
            three.append(value)
         elif index == 4: #it's the fifth pitch class
            five.append(value)
         elif value not in zeros: # it's neither a 1st, 3rd or 5th and it's not already in the 'zeros' list
            zeros.append(value)
      values.sort() # sort them into numerical order
      zeros.sort() # sort them into numerical order
      # with the above preparation, we know the final list will be in order
      octaves = [0, 12, 24, 36, 48, 60, 72, 84, 96, 108]
      for octave in octaves:
         for value in values:
            full_scale.append(octave+value+rootMIDI)
         for value in one:
            all_ones.append(octave+value+rootMIDI)
         for value in three:
            all_threes.append(octave+value+rootMIDI)
         for value in five:
            all_fives.append(octave+value+rootMIDI)
         for value in zeros:
            all_zeros.append(octave+value+rootMIDI)
      self.fullRangedScale = self.cutToPlayerRange(full_scale)
      self.rangedScaleOf1s = self.cutToPlayerRange(all_ones)
      self.rangedScaleOf3s = self.cutToPlayerRange(all_threes)
      self.rangedScaleOf5s = self.cutToPlayerRange(all_fives)
      self.rangedScaleOf0s = self.cutToPlayerRange(all_zeros)

   def cutToPlayerRange(self, valueList):
      resultList = []
      top = self.rangeTop
      bot = self.rangeBottom
      for value in valueList:
         if value > bot and value < top:
            resultList.append(value)
      return resultList

   def pickClosest(self, notepool, target): # returns the nearest note in the notepool to the target
      # check how far the potential notes are from the target
      if len(notepool) > 0:
         differences = [abs(target - float(note)) for note in notepool]
         # find the closest
         closest = differences.index(min(differences))
         return notepool[closest]
      else:
         return -1

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

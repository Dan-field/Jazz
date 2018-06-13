###############################################################
# ManualKeys class by Daniel Field                            #
# This class creates a GUI with a few keys that can be played #
# to a MIDI output.                                           #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

from music import *
from gui import *
from midi import *

class ManualKeys:
   def __init__(self):
      """Initialises a ManualKeys object"""
      self.MOut = MidiOut()
      self.velocity = 80

      # GUI
      self.d = Display("Manual keys", 540, 480, 290, 10, Color(227, 240, 255))
      self.label1 = Label("Velocity: "+str(int(self.velocity)))
      self.slider1 = Slider(HORIZONTAL, 0, 127, int(self.velocity), self.setVelocity)
      self.button1 = Button("A", self.playA)
      self.button2 = Button("B", self.playB)
      self.button3 = Button("C", self.playC)
      self.button4 = Button("D", self.playD)
      self.button5 = Button("E", self.playE)
      self.button6 = Button("F", self.playF)
      self.button7 = Button("G", self.playG)
      self.button8 = Button("A", self.playA2)
      self.button9 = Button("B", self.playB2)
      self.buttonA = Button("C", self.playC2)
      self.d.add(self.label1, 40, 30)
      self.d.add(self.slider1, 40, 60)
      self.d.add(self.button1, 270, 60)
      self.d.add(self.button2, 270, 90)
      self.d.add(self.button3, 270, 120)
      self.d.add(self.button4, 270, 150)
      self.d.add(self.button5, 270, 180)
      self.d.add(self.button6, 310, 60)
      self.d.add(self.button7, 310, 90)
      self.d.add(self.button8, 310, 120)
      self.d.add(self.button9, 310, 150)
      self.d.add(self.buttonA, 310, 180)

   def setVelocity(self, newVelocity):
      self.velocity = int(newVelocity)
      self.label1.setText("Velocity: "+str(newVelocity))

   def playA(self):
      self.MOut.note(57, 0, 1000, self.velocity, 0)
      
   def playB(self):
      self.MOut.note(59, 0, 1000, self.velocity, 0)
      
   def playC(self):
      self.MOut.note(60, 0, 1000, self.velocity, 0)
      
   def playD(self):
      self.MOut.note(62, 0, 1000, self.velocity, 0)
      
   def playE(self):
      self.MOut.note(64, 0, 1000, self.velocity, 0)
      
   def playF(self):
      self.MOut.note(65, 0, 1000, self.velocity, 0)
      
   def playG(self):
      self.MOut.note(67, 0, 1000, self.velocity, 0)
      
   def playA2(self):
      self.MOut.note(69, 0, 1000, self.velocity, 0)
      
   def playB2(self):
      self.MOut.note(71, 0, 1000, self.velocity, 0)
      
   def playC2(self):
      self.MOut.note(72, 0, 1000, self.velocity, 0)

   def weightedChoice(self, weights):
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

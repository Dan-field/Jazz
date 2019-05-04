###############################################################
# MIDI Input class by Daniel Field                            #
#                                                             #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# This class is intended to interface with the KORG nanoKONTROL2
# MIDI input device

from gui import *
from guicontrols import *
from midi import *
from music import *
#from HarmonicStructure import *

class MIDIInput:
   def __init__(self, controller=None):
      """Initialises a MIDI Input object"""
      # set up the class variables
      if controller is None:
         controller = "Unknown vendor nanoKONTROL2"

      # set placeholder for references to other classes
      self.UL = None # placeholder for Urlinie object
      self.LS = None # placeholder for Lead Sheet object
      self.XW = None # placeholder for XMW Writer reference
      self.PP = None # placeholder for Player object
      self.TK = None # placeholder for TimeKeeper object

      # connect to MIDI device
      self.M = MidiIn(controller);
      self.M.hideMessages()

      # set up tempo variables
      self.tempo = 120
      self.volume = 100
      minTempo = 45
      maxTempo = 290
      startTempo = self.tempo
      minVol = 0
      maxVol = 127
      startVol = self.volume
      self.kill = False

      # setup flag to True
      self.isSetup = True
      # note, this is done because the Rotary knob seems to update its value on setup,
      # which negates the attempt to buffer with spaces
       
      # create display
      self.d = Display("KORG nanoKONTROL2 indicator panel", 1000, 350, 10, 260)
       
      # set slider ranges (must be integers)
      self.minVal = 0   # 
      self.maxVal = 127   # 
       
      # create labels
      self.label0 = Label( str(15) + "   ")
      self.label1 = Label( str(self.minVal) + "     ")
      self.label2 = Label( str(self.minVal) + "     ")
      self.label3 = Label( str(self.minVal) + "     ")
      self.label4 = Label( str(self.minVal) + "     ")
      self.label5 = Label( str(self.minVal) + "     ")
      self.label6 = Label( str(self.minVal) + "     ")
      self.label7 = Label( str(self.minVal) + "     ")
      self.label16 = Label( str(self.minVal) + "     ")
      self.label16a = Label("slope")
      self.label17 = Label( str(self.minVal) + "     ")
      self.label17a = Label("arc")
      self.label18 = Label( str(self.minVal) + "     ")
      self.label18a = Label("und no.")
      self.label19 = Label( str(self.minVal) + "     ")
      self.label19a = Label("und grd")
      self.label20 = Label( str(self.minVal) + "     ")
      self.label20a = Label("step")
      self.label21 = Label( str(self.minVal) + "     ")
      self.label21a = Label("wait")
      self.label22 = Label( str(self.minVal) + "     ")
      self.label22a = Label("d/beat")
      self.label23 = Label( str(self.minVal) + "     ")
      self.label23a = Label("I end")
      self.labelT1 = Label("Tempo: "+str(self.tempo)+" bpm")
      self.labelT2 = Label("Vol: "+str(self.volume))

      # next, create two slider widgets and assign their callback functions
      #Slider(orientation, lower, upper, start, eventHandler)
      self.slider0 = Slider(VERTICAL, self.minVal, self.maxVal, 15, self.setValue0)
      self.slider1 = Slider(VERTICAL, self.minVal, self.maxVal, self.minVal, self.setValue1)
      self.slider2 = Slider(VERTICAL, self.minVal, self.maxVal, self.minVal, self.setValue2)
      self.slider3 = Slider(VERTICAL, self.minVal, self.maxVal, self.minVal, self.setValue3)
      self.slider4 = Slider(VERTICAL, self.minVal, self.maxVal, self.minVal, self.setValue4)
      self.slider5 = Slider(VERTICAL, self.minVal, self.maxVal, self.minVal, self.setValue5)
      self.slider6 = Slider(VERTICAL, self.minVal, self.maxVal, self.minVal, self.setValue6)
      self.slider7 = Slider(VERTICAL, self.minVal, self.maxVal, self.minVal, self.setValue7)
      self.sliderT1 = Slider(HORIZONTAL, minTempo, maxTempo, startTempo, self.setTempo)
      self.sliderT2 = Slider(HORIZONTAL, minVol, maxVol, startVol, self.setVolume)
      self.buttonT1 = Button("kill", self.killTimer)
      self.rotary16 = Rotary(525, 40, 565, 80, self.minVal, self.maxVal, self.maxVal/2, self.setValue16, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary17 = Rotary(575, 40, 615, 80, self.minVal, self.maxVal, self.maxVal*3/4, self.setValue17, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary18 = Rotary(625, 40, 665, 80, self.minVal, self.maxVal, self.minVal, self.setValue18, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary19 = Rotary(675, 40, 715, 80, self.minVal, self.maxVal, self.maxVal/2, self.setValue19, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary20 = Rotary(725, 40, 765, 80, self.minVal, self.maxVal, 58, self.setValue20, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary21 = Rotary(775, 40, 815, 80, self.minVal, self.maxVal, self.minVal, self.setValue21, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary22 = Rotary(825, 40, 865, 80, self.minVal, self.maxVal, 127, self.setValue22, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary23 = Rotary(875, 40, 915, 80, self.minVal, self.maxVal, 127, self.setValue23, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
       
      # add labels and sliders to display
      self.d.add(self.label0, 540, 95)
      self.d.add(self.slider0, 540, 110)
      self.d.add(self.label1, 590, 95)
      self.d.add(self.slider1, 590, 110)
      self.d.add(self.label2, 640, 95)
      self.d.add(self.slider2, 640, 110)
      self.d.add(self.label3, 690, 95)
      self.d.add(self.slider3, 690, 110)
      self.d.add(self.label4, 740, 95)
      self.d.add(self.slider4, 740, 110)
      self.d.add(self.label5, 790, 95)
      self.d.add(self.slider5, 790, 110)
      self.d.add(self.label6, 840, 95)
      self.d.add(self.slider6, 840, 110)
      self.d.add(self.label7, 890, 95)
      self.d.add(self.slider7, 890, 110)
      self.d.add(self.rotary16)
      self.d.add(self.label16, 540, 20)
      self.d.add(self.label16a, 540, 10)
      self.d.add(self.rotary17)
      self.d.add(self.label17, 590, 20)
      self.d.add(self.label17a, 590, 10)
      self.d.add(self.rotary18)
      self.d.add(self.label18, 640, 20)
      self.d.add(self.label18a, 640, 10)
      self.d.add(self.rotary19)
      self.d.add(self.label19, 690, 20)
      self.d.add(self.label19a, 690, 10)
      self.d.add(self.rotary20)
      self.d.add(self.label20, 740, 20)
      self.d.add(self.label20a, 740, 10)
      self.d.add(self.rotary21)
      self.d.add(self.label21, 790, 20)
      self.d.add(self.label21a, 790, 10)
      self.d.add(self.rotary22)
      self.d.add(self.label22, 840, 20)
      self.d.add(self.label22a, 840, 10)
      self.d.add(self.rotary23)
      self.d.add(self.label23, 890, 20)
      self.d.add(self.label23a, 890, 10)
      self.d.add(self.labelT1, 40, 30)
      self.d.add(self.sliderT1, 40, 60)
      self.d.add(self.labelT2, 40, 120)
      self.d.add(self.sliderT2, 40, 150)
      self.d.add(self.buttonT1, 40, 210)

      # setup is finished
      self.isSetup = False

      # start up MIDI listener
      self.M.onInput(176, self.incoming);

   def setUrlinieReference(self, reference):
      self.UL = reference

   def setLeadSheetReference(self, reference):
      self.LS = reference

   def setXMLWriterReference(self, reference):
      self.XW = reference

   def setPlayerReference(self, reference):
      self.PP = reference

   def setTimeKeeperReference(self, reference):
      self.TK = reference

   # define callback functions (called every time the slider changes)
   def setValue0(self, value):   # function to change frequency
      # global label0      # label to update
      self.label0.setText(str(value))
   def setValue1(self, value):   # function to change frequency
      # global label1      # label to update
      self.label1.setText(str(value))  # update label
   def setValue2(self, value):   # function to change frequency
      # global label2      # label to update
      self.label2.setText(str(value))  # update label
   def setValue3(self, value):   # function to change frequency
      # global label3      # label to update
      self.label3.setText(str(value))  # update label
   def setValue4(self, value):   # function to change frequency
      # global label4      # label to update
      self.label4.setText(str(value))  # update label
   def setValue5(self, value):   # function to change frequency
      # global label5      # label to update
      self.label5.setText(str(value))  # update label
   def setValue6(self, value):   # function to change frequency
      # global label6      # label to update
      self.label6.setText(str(value))  # update label
   def setValue7(self, value):   # function to change frequency
      # global label7      # label to update
      self.label7.setText(str(value))  # update label
   def setValue16(self, value):
      # global label16
      if self.isSetup:
         self.label16.setText(str(self.maxVal/2)+"   ")
      else:
         self.label16.setText(str(value))
   def setValue17(self, value):
      # global label17
      if self.isSetup:
         self.label17.setText(str(self.maxVal*3/4)+"   ")
      else:
         self.label17.setText(str(value))
   def setValue18(self, value):
      # global label18
      if self.isSetup:
         self.label18.setText("0    ")
      else:
         self.label18.setText(str(value))
   def setValue19(self, value):
      # global label19
      if self.isSetup:
         self.label19.setText(str(self.maxVal/2)+"   ")
      else:
         self.label19.setText(str(value))
   def setValue20(self, value):
      # global label20
      if self.isSetup:
         self.label20.setText(str(58)+"   ")
      else:
         self.label20.setText(str(value))
   def setValue21(self, value):
      # global label21
      if self.isSetup:
         self.label21.setText("0    ")
      else:
         self.label21.setText(str(value))
   def setValue22(self, value):
      # global label22
      if self.isSetup:
         self.label22.setText("0    ")
      else:
         self.label22.setText(str(value))
   def setValue23(self, value):
      # global label23
      if self.isSetup:
         self.label23.setText(str(127)+"  ")
      else:
         self.label23.setText(str(value))

   def setTempo(self, newTempo):
      if self.TK is not None:
         self.TK.setTempo(newTempo)
      self.labelT1.setText("Tempo: "+str(newTempo)+" bpm")
      self.tempo = newTempo
      
   def setVolume(self, newVolume):
      self.volume = newVolume
      self.labelT2.setText("Vol: "+str(newVolume))
      
   def killTimer(self):
      self.kill = True
      if self.TK is not None:
         self.TK.kill()
      if self.XW is not None:
         self.XW.endPart()
         self.XW.endXMLFile()
   
    

   # define MIDI device slider callback
   def incoming(self, eventType, channel, data1, data2):
      if data1 == 0:
         self.slider0.setValue(data2)
         self.PP.setULScaleDegreeWeights(data2)
      elif data1 ==1:
         self.slider1.setValue(data2)
      elif data1 ==2:
         self.slider2.setValue(data2)
      elif data1 ==3:
         self.slider3.setValue(data2)
      elif data1 ==4:
         self.slider4.setValue(data2)
      elif data1 ==5:
         self.slider5.setValue(data2)
      elif data1 ==6:
         self.slider6.setValue(data2)
      elif data1 ==7:
         self.slider7.setValue(data2)
      elif data1 == 16:
         self.rotary16.setValue(data2)
         self.UL.adjustOverallSlope(data2)
      elif data1 == 17:
         self.rotary17.setValue(data2)
         self.UL.adjustArcMultiplier(data2)
      elif data1 == 18:
         self.rotary18.setValue(data2)
         self.UL.adjustNumberOfUndulations(data2)
      elif data1 == 19:
         self.rotary19.setValue(data2)
         self.UL.adjustUndulationGradient(data2)
      elif data1 == 20:
         self.rotary20.setValue(data2)
         self.PP.setULJump(data2)
      elif data1 == 21:
         self.rotary21.setValue(data2)
         self.PP.setULBeatWait(data2)
      elif data1 == 22:
         self.rotary22.setValue(data2)
         self.PP.setDownBeatAffinity(data2)
      elif data1 == 23:
         self.rotary23.setValue(data2)
         self.PP.setIAffinity(data2)

   def tick(self, ls):
      ls.Tick()

   def getTempo(self):
      return self.tempo

   def startTimer(self):
      # run the central counter
      while(self.kill == False):
         self.tick(self.LS)
         sleep(5.0/self.tempo) # this is (60.0/tempo)/12 since there are 12 ticks per beat
         
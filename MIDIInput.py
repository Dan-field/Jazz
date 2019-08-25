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
   def __init__(self, DS=1.0, controller=None):
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
      self.NS = None # placeholder for NoteSender object

      # connect to MIDI device
      self.M = MidiIn(controller);
      self.M.hideMessages()

      # set up tempo variables
      self.tempo = 120
      self.volume = 100
      self.swinging = False
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
      self.d = Display("KORG nanoKONTROL2 indicator panel", int(1000*DS), int(350*DS), int(10*DS), int(260*DS))

      # create timer
      self.t = Timer(int(5000.0/self.tempo), self.tick, [self.LS], True) # this is (60000.0/tempo)/12 since there are 12 ticks per beat
       
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
      self.labelSw = Label("Swing")
      self.labelAcc = Label("Accompany")

      # set fonts for labels
      self.fontChoice = Font("SansSerif", Font.PLAIN, int(14*DS))
      self.fontBigger = Font("SansSerif", Font.BOLD, int(18*DS))
      self.label0.setFont(self.fontChoice)
      self.label1.setFont(self.fontChoice)
      self.label2.setFont(self.fontChoice)
      self.label3.setFont(self.fontChoice)
      self.label4.setFont(self.fontChoice)
      self.label5.setFont(self.fontChoice)
      self.label6.setFont(self.fontChoice)
      self.label7.setFont(self.fontChoice)
      self.label16.setFont(self.fontChoice)
      self.label16a.setFont(self.fontChoice)
      self.label17.setFont(self.fontChoice)
      self.label17a.setFont(self.fontChoice)
      self.label18.setFont(self.fontChoice)
      self.label18a.setFont(self.fontChoice)
      self.label19.setFont(self.fontChoice)
      self.label19a.setFont(self.fontChoice)
      self.label20.setFont(self.fontChoice)
      self.label20a.setFont(self.fontChoice)
      self.label21.setFont(self.fontChoice)
      self.label21a.setFont(self.fontChoice)
      self.label22.setFont(self.fontChoice)
      self.label22a.setFont(self.fontChoice)
      self.label23.setFont(self.fontChoice)
      self.label23a.setFont(self.fontChoice)
      self.labelT1.setFont(self.fontBigger)
      self.labelT2.setFont(self.fontBigger)
      self.labelSw.setFont(self.fontBigger)
      self.labelAcc.setFont(self.fontBigger)

      # next, create two slider widgets and assign their callback functions
      #Slider(orientation, lower, upper, start, eventHandler)
      self.slider0 = Slider(VERTICAL, self.minVal, self.maxVal, 15, self.setValue0)
      self.slider1 = Slider(VERTICAL, self.minVal, self.maxVal, self.minVal, self.setValue1)
      self.slider2 = Slider(VERTICAL, self.minVal, self.maxVal, 94, self.setValue2)
      self.slider3 = Slider(VERTICAL, self.minVal, self.maxVal, 63, self.setValue3) # note density
      self.slider4 = Slider(VERTICAL, self.minVal, self.maxVal, 127, self.setValue4) # beat heirarchy
      self.slider5 = Slider(VERTICAL, self.minVal, self.maxVal, self.minVal, self.setValue5)
      self.slider6 = Slider(VERTICAL, self.minVal, self.maxVal, self.minVal, self.setValue6)
      self.slider7 = Slider(VERTICAL, self.minVal, self.maxVal, self.minVal, self.setValue7)
      self.sliderT1 = Slider(HORIZONTAL, minTempo, maxTempo, startTempo, self.setTempo)
      self.sliderT2 = Slider(HORIZONTAL, minVol, maxVol, startVol, self.setVolume)
      self.buttonT1 = Button("Write / Restart", self.killTimer)
      self.rotary16 = Rotary(int(525*DS), int(40*DS), int(565*DS), int(80*DS), self.minVal, self.maxVal, self.maxVal/2, self.setValue16, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary17 = Rotary(int(575*DS), int(40*DS), int(615*DS), int(80*DS), self.minVal, self.maxVal, self.maxVal*3/4, self.setValue17, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary18 = Rotary(int(625*DS), int(40*DS), int(665*DS), int(80*DS), self.minVal, self.maxVal, self.minVal, self.setValue18, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary19 = Rotary(int(675*DS), int(40*DS), int(715*DS), int(80*DS), self.minVal, self.maxVal, self.maxVal/2, self.setValue19, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary20 = Rotary(int(725*DS), int(40*DS), int(765*DS), int(80*DS), self.minVal, self.maxVal, 58, self.setValue20, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary21 = Rotary(int(775*DS), int(40*DS), int(815*DS), int(80*DS), self.minVal, self.maxVal, self.minVal, self.setValue21, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary22 = Rotary(int(825*DS), int(40*DS), int(865*DS), int(80*DS), self.minVal, self.maxVal, 127, self.setValue22, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.rotary23 = Rotary(int(875*DS), int(40*DS), int(915*DS), int(80*DS), self.minVal, self.maxVal, 127, self.setValue23, Color(50, 110, 255), Color(240, 240, 240), Color(210, 210, 210), 1, 360)
      self.toggleSw = Toggle(int(350*DS), int(40*DS), int(390*DS), int(80*DS), False, self.toggleSwing, Color.BLUE, Color.WHITE, Color(50, 110, 255))
      self.toggleAcc = Toggle(int(350*DS), int(90*DS), int(390*DS), int(130*DS), False, self.toggleAccompaniment, Color.BLUE, Color.WHITE, Color(50, 110, 255))
       
      # add labels and sliders to display
      self.d.add(self.label0, int(540*DS), int(95*DS))
      self.d.add(self.slider0, int(540*DS), int(110*DS))
      self.d.add(self.label1, int(590*DS), int(95*DS))
      self.d.add(self.slider1, int(590*DS), int(110*DS))
      self.d.add(self.label2, int(640*DS), int(95*DS))
      self.d.add(self.slider2, int(640*DS), int(110*DS))
      self.d.add(self.label3, int(690*DS), int(95*DS))
      self.d.add(self.slider3, int(690*DS), int(110*DS))
      self.d.add(self.label4, int(740*DS), int(95*DS))
      self.d.add(self.slider4, int(740*DS), int(110*DS))
      self.d.add(self.label5, int(790*DS), int(95*DS))
      self.d.add(self.slider5, int(790*DS), int(110*DS))
      self.d.add(self.label6, int(840*DS), int(95*DS))
      self.d.add(self.slider6, int(840*DS), int(110*DS))
      self.d.add(self.label7, int(890*DS), int(95*DS))
      self.d.add(self.slider7, int(890*DS), int(110*DS))
      self.d.add(self.rotary16)
      self.d.add(self.label16, int(540*DS), int(20*DS))
      self.d.add(self.label16a, int(540*DS), int(3*DS))
      self.d.add(self.rotary17)
      self.d.add(self.label17, int(590*DS), int(20*DS))
      self.d.add(self.label17a, int(590*DS), int(3*DS))
      self.d.add(self.rotary18)
      self.d.add(self.label18, int(640*DS), int(20*DS))
      self.d.add(self.label18a, int(640*DS), int(3*DS))
      self.d.add(self.rotary19)
      self.d.add(self.label19, int(690*DS), int(20*DS))
      self.d.add(self.label19a, int(690*DS), int(3*DS))
      self.d.add(self.rotary20)
      self.d.add(self.label20, int(740*DS), int(20*DS))
      self.d.add(self.label20a, int(740*DS), int(3*DS))
      self.d.add(self.rotary21)
      self.d.add(self.label21, int(790*DS), int(20*DS))
      self.d.add(self.label21a, int(790*DS), int(3*DS))
      self.d.add(self.rotary22)
      self.d.add(self.label22, int(840*DS), int(20*DS))
      self.d.add(self.label22a, int(840*DS), int(3*DS))
      self.d.add(self.rotary23)
      self.d.add(self.label23, int(890*DS), int(20*DS))
      self.d.add(self.label23a, int(890*DS), int(3*DS))
      self.d.add(self.labelT1, int(40*DS), int(30*DS))
      self.d.add(self.sliderT1, int(40*DS), int(60*DS))
      self.d.add(self.labelT2, int(40*DS), int(120*DS))
      self.d.add(self.sliderT2, int(40*DS), int(150*DS))
      self.d.add(self.buttonT1, int(40*DS), int(210*DS))
      self.d.add(self.toggleSw)
      self.d.add(self.labelSw, int(400*DS), int(46*DS))
      self.d.add(self.toggleAcc)
      self.d.add(self.labelAcc, int(400*DS), int(96*DS))

      # setup is finished
      self.isSetup = False

      # start up MIDI listener
      self.M.onInput(176, self.incoming);

   def setUrlinieReference(self, reference):
      self.UL = reference

   def setLeadSheetReference(self, reference):
      self.LS = reference
      self.t.setFunction(self.tick, [self.LS])

   def setXMLWriterReference(self, reference):
      self.XW = reference

   def setPlayerReference(self, reference):
      self.PP = reference

   def setTimeKeeperReference(self, reference):
      self.TK = reference

   def setNoteSenderReference(self, reference):
      self.NS = reference

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
      #if self.TK is not None:
      #   self.TK.setTempo(newTempo)
      self.labelT1.setText("Tempo: "+str(newTempo)+" bpm")
      self.tempo = newTempo
      self.t.setDelay(int(5000.0/newTempo))
      
   def setVolume(self, newVolume):
      self.volume = newVolume
      self.labelT2.setText("Vol: "+str(newVolume))
      
   def killTimer(self):
      if self.kill == False:
         self.kill = True
         self.t.stop()
         self.NS.showNoteLists()
      else:
         self.kill = False
         self.t.start()
      #if self.XW is not None:
      #   self.XW.endPart()
      #   self.XW.endXMLFile()
   
   def toggleSwing(self, value):
      self.swinging = value
      self.PP.setSwinging(value)

   def toggleAccompaniment(self, value):
      self.LS.accompany = value

   # define MIDI device slider callback
   def incoming(self, eventType, channel, data1, data2):
      if data1 == 0:
         self.slider0.setValue(data2)
         self.PP.setScaleDegreeWeights(data2)
      elif data1 ==1:
         self.slider1.setValue(data2)
         self.PP.setMotifShape(data2)
      elif data1 ==2:
         self.slider2.setValue(data2)
         self.PP.setMotifScale(64-data2)
      elif data1 ==3:
         self.slider3.setValue(data2)
         self.PP.setNoteDensity(data2)
      elif data1 ==4:
         self.slider4.setValue(data2)
         self.PP.setBeatHeirarchy(data2)
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
      # send the tick on to the LeadSheet
      if ls is not None:
         ls.Tick()

   def nextZero(self):
      # the next tick will be the start of the next beat
      if self.swinging:
         # swing is set to on, so the tick timer needs to be adjusted
         # using a 62/38 ratio for swing
         # ticks need to be adjusted by a factor of 62:50
         self.t.setDelay(int(5000.0*62.0/(self.tempo*50.0)))
         # note: I'm assuming the new delay value will take effect at the NEXT timer run

   def nextQuav(self):
      # the next tick will be the start of the second quaver beat
      if self.swinging:
         # swing is set to on, so the tick timer needs to be adjusted
         # using a 62/38 ratio for swing
         # ticks need to be adjusted by a factor of 38:50
         self.t.setDelay(int(5000.0*38.0/(self.tempo*50.0)))
         # note: I'm assuming the new delay value will take effect at the NEXT timer run

   def getTempo(self):
      return self.tempo

   def startTimer(self):
      # run the central counter
      self.t.start()
      #while(self.kill == False):
      #   self.tick(self.LS)
      #   sleep(5.0/self.tempo) # this is (60.0/tempo)/12 since there are 12 ticks per beat
         
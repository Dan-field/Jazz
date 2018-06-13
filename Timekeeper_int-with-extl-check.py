#################################################################
# Timekeeper class by Daniel Field                              #
# This class keeps time for the algorithmic soloist             #
# It includes routines to synchronise with an external downbeat #
# check out www.github.com/dan-field/jazz for info and rights   #
#################################################################

from time import *
from thread import *
from threading import *
from gui import *
from midi import *

class Timekeeper:
   def __init__(self, UsrStartTempo=None, UsrBeatsPerBar=None, UsrOSCInput=None): #UsrStartTempo should be an integer, but a float will work too
      """Initialises a Timekeeper object"""
      if UsrStartTempo is not None:
         self.tempo = int(UsrStartTempo)
      else:
         self.tempo = 120
      if UsrBeatsPerBar is not None:
         self.bpb = int(UsrBeatsPerBar)
      else:
         self.bpb = 1
      if UsrOSCInput is not None:
         self.OSC_In = UsrOSCInput
      else:
         self.OSC_In = None
      self.divisions = 4
      self.beat = 0
      self.minTempo = 45
      self.maxTempo = 290
      self.tempo_adjusted = self.tempo
      self.latency = 39 # manual latency in milliseconds
      self.kill = False
      self.TapTime_Internal = 0.0
      self.TapTime_Int_previous = 0.0
      self.TapTime_External = 0.0
      self.TapTime_Ext_previous = 0.0
      self.timingError = 0.0
      self.timingErrorCumulative = 0.0
      self.timeSmoothingFactor = 0.05 # 0.0 provides no smoothing, max 1.0. Tip: keep this pretty low. Higher values are intended to handle source jitter and should not be needed if the external source is good.
      self.timesource_is_external = False
      self.Player = None

      # GUI
      self.d = Display("Timekeeper", 540, 960, 20, 200, Color(227, 240, 255))
      self.label1 = Label("Tempo: "+str(self.tempo)+"   bpm ")
      self.label2 = Label("Latency: "+str(self.latency)+"  ms  ")
      self.label4 = Label("Beats per Bar: "+str(int(self.bpb))+"/"+str(int(self.divisions)))
      self.label3 = Label("Smoothness of TEMPO following")
      self.slider1 = Slider(HORIZONTAL, self.minTempo, self.maxTempo, self.tempo, self.setTempo)
      self.slider2 = Slider(HORIZONTAL, 0, 500, self.latency, self.setLatency)
      self.slider3 = Slider(HORIZONTAL, 0, 100, int(self.timeSmoothingFactor*100), self.setSmoothingFactor)
      self.checkbox1 = Checkbox("External Timesource", self.setExtTimeSrc)
      self.checkbox2 = Checkbox("Stop Metronome", self.setKill)
      self.d.add(self.label1, 80, 60)
      self.d.add(self.slider1, 80, 120)
      self.d.add(self.label2, 80, 180)
      self.d.add(self.slider2, 80,240)
      self.d.add(self.label4, 320, 60)
      self.d.add(self.slider3, 80, 360)
      self.d.add(self.label3, 80, 300)
      self.d.add(self.checkbox1, 80, 480)
      self.d.add(self.checkbox2, 80, 540)

      # MIDI
      self.MOut = MidiOut()
      self.velocity = 40

   def setTempo(self, newTempo):
      self.tempo = int(newTempo)
      self.label1.setText("Tempo: "+str(int(newTempo))+" bpm")
      if self.timesource_is_external is False: # we want to adjust the tempo manually
         self.tempo_adjusted = self.tempo

   def setBPB(self, newBPB):
      self.bpb = int(newBPB)
      self.label4.setText("Beats per Bar: "+str(int(newBPB))+"/"+str(self.divisions))

   def setDivisions(self, newDivisions):
      self.divisions = int(newDivisions)
      self.label4.setText("Beats per Bar: "+str(int(self.bpb))+"/"+str(int(newDivisions)))

   def setDownbeatExternal(self, newTime):
      self.TapTime_Ext_previous = self.TapTime_External
      self.TapTime_External = newTime-(0.001*self.latency)

   def setSmoothingFactor(self, newSmoothingFactor):
      self.timeSmoothingFactor = 0.01*newSmoothingFactor

   def setLatency(self, newLatency):
      self.latency = newLatency
      self.label2.setText("Latency: "+str(newLatency)+"  ms  ")

   def setExtTimeSrc(self, newSetting):
      self.timesource_is_external = newSetting
      if newSetting == False:
         self.TapTime_Internal = 0.0
         self.TapTime_Int_previous = 0.0
         self.TapTime_External = 0.0
         self.TapTime_Ext_previous = 0.0

   def setKill(self, newKill):
      self.kill = newKill

   def getWaitTime(self):
      return 60.0/self.tempo

   def setPlayer(self, newPlayer):
      self.Player = newPlayer

   def metronome(self):
      if self.kill == False: # metronome stops counting if Kill is true
         self.beat += 1
         note = 59
         # do the AUTOMATIC tempo updates on the DOWNBEAT (to coincide with the incoming downbeat signal)
         if self.beat > self.bpb:
            self.beat = 1
            note = 71
            self.TapTime_Int_previous = self.TapTime_Internal
            self.TapTime_Internal = time()
            if self.timesource_is_external:
               #self.TapTime_External = self.OSC_In.getDownbeatTime()-(0.001*self.latency)
               self.calculateTimeError() # on every metronome downbeat
               self.updateEffectiveTempo() # after calculating the time error
         self.tap(note) # look after the musical aspects

   def tap(self, note):
      #print "tap "+str(self.beat)
      # this function will define what happens (musically) at each beat
      # for now, it's just tapping audibly
      self.MOut.note(int(note), 0, 40, self.velocity, 0) # pitch, channel, duration (ms), velocity, start time
      if self.Player is not None:
         self.Player.beat(self.beat, self.tempo)

   def calculateTimeError(self): # assumption: this is called at every downbeat
      if self.TapTime_Internal == 0.0 or self.TapTime_External == 0.0:
         self.timingError = 0.0
         if self.TapTime_Internal == 0.0:
            print "no error calculation (no INTERNAL tap time)"
         if self.TapTime_External == 0.0:
            print "no error calculation (no EXTERNAL tap time)"
      else:
         Expected_next_DB = self.TapTime_External+(60.0*self.bpb/self.tempo) # expected NEXT downbeat time based on the latest downbeat time and the tempo
         Error1 = abs(self.TapTime_Internal - Expected_next_DB) # This is how far ahead of the NEXT downbeat we are
         Error2 = abs(self.TapTime_Internal - self.TapTime_External) # This is how far behind the LATEST downbeat we are
         # We want to pick the closer of the two as our error, i.e. either speed up or slow down to meet the closest downbeat
         if Error1 < Error2: # we're better off speeding up
            self.timingError = self.TapTime_Internal - Expected_next_DB
         else: # we're better off slowing down
            self.timingError = self.TapTime_Internal - self.TapTime_External
         self.timingErrorCumulative = self.timeSmoothingFactor*self.timingErrorCumulative + (1.0-self.timeSmoothingFactor)*self.timingError
         #print "timing error is "+str(self.timingError)+" sec"
         #print "smoothed error is "+str(self.timingErrorCumulative)+" sec"

   def updateEffectiveTempo(self):
      adjustment_time = 0.25*self.timingErrorCumulative
      nominal_time = 60.0/self.tempo
      required_time = nominal_time-adjustment_time
      self.tempo_adjusted = 60.0/required_time

   def startTimer(self):
      self.metronome()
#####################################################################
# Timekeeper class by Daniel Field                                  #
# This class keeps time for the algorithmic soloist                 #
# It includes routines to synchronise with an external downbeat     #
# 10th June 2018 - changing base count to 16                        #
# 12th June 2018 - changing operation to slave to external downbeat #
# check out www.github.com/dan-field/jazz for info and rights       #
#####################################################################

from time import *
from thread import *
from timer import *
#from threading import Timer
from gui import *
#from midi import *

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
         self.bpb = 4
      if UsrOSCInput is not None:
         self.OSC_In = UsrOSCInput
      else:
         self.OSC_In = None
      self.divisions = 4
      self.beat = 0
      self.count16 = -1
      self.lastBeat = False
      self.minTempo = 45
      self.maxTempo = 290
      self.adjusted_16count = self.tempo*4
      self.latency = -110 # auto latency in milliseconds
      self.tempo_adjustment = 0 # manual adjustment of latency
      self.kill = False
      self.TapTime_Internal = 0.0
      self.TapTime_Int_previous = 0.0
      self.TapTime_External = 0.0
      self.TapTime_Ext_previous = 0.0
      self.timingError = 0.0
      self.timingErrorCumulative = 0.0
      self.timeSmoothingFactor = 0.0 # 0.0 provides no smoothing, max 1.0. Tip: keep this pretty low. Higher values are intended to handle source jitter and should not be needed if the external source is good.
      self.timesource_is_external = False
      self.isMuted = False
      self.muteThresh = 40
      self.Player = None

      # GUI
      self.d = Display("Timekeeper", 540, 960, 20, 200, Color(227, 240, 255))
      self.label1 = Label("Tempo: "+str(self.tempo)+"   qn/m  ")
      self.label2 = Label("Tempo: manual fine adjust")
      self.label4 = Label("Beats per Bar: "+str(int(self.bpb))+"/"+str(int(self.divisions))+"  ")
      self.label3 = Label("Smoothness of TEMPO following")
      self.label5 = Label("Muting Threshold: "+str(self.muteThresh)+"  ms  ")
      self.slider1 = Slider(HORIZONTAL, self.minTempo, self.maxTempo, self.tempo, self.setTempo)
      self.slider2 = Slider(HORIZONTAL, -100, 100, self.tempo_adjustment, self.setTempoAdjustment)
      self.slider3 = Slider(HORIZONTAL, 0, 1000, int(self.timeSmoothingFactor*100000), self.setSmoothingFactor)
      self.slider4 = Slider(HORIZONTAL, 0, 200, self.muteThresh, self.setMuteThresh)
      self.checkbox1 = Checkbox("External Timesource", self.setExtTimeSrc)
      self.checkbox2 = Checkbox("Stop Metronome", self.setKill)
      self.checkbox3 = Checkbox("Mute", self.setMute)
      self.checkbox3.check()
      self.d.add(self.label1, 80, 60)
      self.d.add(self.slider1, 80, 120)
      self.d.add(self.label2, 80, 180)
      self.d.add(self.slider2, 80,240)
      self.d.add(self.label4, 320, 60)
      self.d.add(self.slider3, 80, 480)
      self.d.add(self.label3, 80, 420)
      self.d.add(self.slider4, 80, 360)
      self.d.add(self.label5, 80, 300)
      self.d.add(self.checkbox1, 80, 600)
      #self.d.add(self.checkbox2, 80, 660)
      self.d.add(self.checkbox3, 320, 120)

      # TIMER
      self.t = Timer(500, self.metronome, (), True) # this is a recurring timer (note, JEM timer is not the same as Python Timer)

      # MIDI
      #self.MOut = MidiOut()
      #self.velocity = 0 # set to zero to mute the piano tap

   def setTempoAdjustment(self, newValue):
      self.tempo_adjustment = newValue

   def setTempo(self, newTempo):
      self.tempo = int(newTempo)
      self.label1.setText("Tempo: "+str(int(newTempo))+" bpm  ")
      if self.timesource_is_external is False: # we want to adjust the tempo manually
         self.adjusted_16count = self.tempo*4
         self.setLatency(int(0.65*self.tempo) - 230)

   def setBPB(self, newBPB):
      self.bpb = int(newBPB)
      self.label4.setText("Beats per Bar: "+str(int(newBPB))+"/"+str(self.divisions))

   def setDivisions(self, newDivisions):
      self.divisions = int(newDivisions)
      self.label4.setText("Beats per Bar: "+str(int(self.bpb))+"/"+str(int(newDivisions)))

   def setDownbeatExternal(self, newTime):
      self.TapTime_Ext_previous = self.TapTime_External
      self.TapTime_External = newTime-(0.001*self.latency)
      self.count16 = -1
      self.beat = 0
      self.adjusted_16count = self.tempo*4
      self.metronome()

   def setSmoothingFactor(self, newSmoothingFactor):
      self.timeSmoothingFactor = 0.01*newSmoothingFactor

   def setLatency(self, newLatency):
      self.latency = newLatency

   def setMuteThresh(self, newThreshold):
      self.muteThresh = newThreshold
      self.label5.setText("Muting Threshold: "+str(int(newThreshold))+"  ms")

   def setMute(self, newMute):
      self.isMuted = newMute
      if self.Player is not None:
         self.Player.setMute(newMute)

   def setExtTimeSrc(self, newSetting):
      self.timesource_is_external = newSetting
      if newSetting == True:
         self.isMuted = True
      if newSetting == False:
         self.isMuted = False
         self.TapTime_Internal = 0.0
         self.TapTime_Int_previous = 0.0
         self.TapTime_External = 0.0
         self.TapTime_Ext_previous = 0.0

   def setKill(self, newKill):
      self.kill = newKill

   def setPlayer(self, newPlayer):
      self.Player = newPlayer

   def metronome_new(self):
      if self.kill is False:
         self.adjusted_16count = self.tempo*4
         self.t.stop()
         required_delay = int(60000.0/self.adjusted_16count)
         if self.count16 == 0:
            required_delay += self.latency
            if required_delay < 0:
               required_delay = 0
         self.t.setDelay(required_delay)
         self.t.setRepeat(True)
         self.count16 += 1
         if self.count16%(16/self.divisions) == 0: # this is a recognised beat
            self.beat +=1
         #   if self.beat > self.bpb: # too many beats in this bar
         #      self.t.stop() # stop, nothing will happend until another downbeat comes in
         self.tap(64)

   def metronome_newBar(self):
      if self.kill is False:
         self.count16 = 0
         self.tap(64)
         self.metronome()

   def metronome(self):
      if self.kill is False:
         self.adjusted_16count = self.tempo*4
         #self.t.setRepeat(False)
         self.t.stop() # this doesn't always seem to be working
         self.t.stop()
         self.t.stop()
         self.t.stop()
         self.t.stop()
         self.t.stop()
         self.count16 += 1
         self.tap(64)
         reference = 60000.0+(60.0*self.tempo_adjustment) # tempo_adjustment is between -100 and +100
         required_delay = int(reference/self.adjusted_16count)
         if self.count16 == 0:
            required_delay -= self.latency
            if required_delay < 0:
               required_delay = 0
         #self.t.setDelay(required_delay)
         self.t = Timer(required_delay, self.metronome, (), False)
         self.t.start()
         if self.count16%(16/self.divisions) == 0: # this is a recognised beat
            self.beat +=1
            if self.beat > self.bpb: # too many beats in this bar
               self.t.stop() # stop, nothing will happen until another downbeat comes in
         self.Player.tap16th()

   def metronome_old2(self):
      if self.kill is False: # metronome stops counting if Kill is true
         self.count16 +=1 # counting 16th counts
         if self.count16%(16/self.divisions) == 0: # this is an actual beat
            self.beat += 1
            note = 59
            # do the AUTOMATIC tempo updates on the DOWNBEAT (to coincide with the incoming downbeat signal)
            if self.beat > self.bpb:
               self.beat = 1
               self.count16 = 0
               note = 71
               self.TapTime_Int_previous = self.TapTime_Internal
               self.TapTime_Internal = time()
               if self.timesource_is_external:
                  #self.TapTime_External = self.OSC_In.getDownbeatTime()-(0.001*self.latency)
                  self.calculateTimeError() # on every metronome downbeat
                  self.updateEffectiveTempo() # after calculating the time error
            #self.tap(note) # look after the musical aspects

   def tap(self, note):
      if self.Player is not None:
         if self.beat == self.bpb:
            self.lastBeat = True
         else:
            self.lastBeat = False
         self.Player.beat(self.count16, self.tempo, self.lastBeat)
      #if ((self.count16-1)%(16/self.divisions)) == 0:
      #   self.MOut.note(int(note), 0, 40, self.velocity, 0) # pitch, channel, duration (ms), velocity, start time

   def tap16th(self):
      self.Player.tap16th()

   def calculateTimeError(self): # assumption: this is called at every downbeat
      if self.TapTime_Internal == 0.0 or self.TapTime_External == 0.0:
         self.timingError = 0.0
         if self.TapTime_Internal == 0.0:
            print "no error calculation (no INTERNAL tap time)"
         if self.TapTime_External == 0.0:
            print "no error calculation (no EXTERNAL tap time)"
      else:
         bar_duration = (60.0/self.tempo)*(self.bpb*4.0/self.divisions)
         Expected_next_DB = self.TapTime_External+bar_duration # expected NEXT downbeat time based on the latest downbeat time and the tempo
         Error1 = abs(self.TapTime_Internal - Expected_next_DB) # This is how far ahead of the NEXT downbeat we are - NEGATIVE number
         Error2 = abs(self.TapTime_Internal - self.TapTime_External) # This is how far behind the LATEST downbeat we are - POSITIVE number
         # We want to pick the closer of the two as our error, i.e. either speed up or slow down to meet the closest downbeat
         if Error1 < Error2: # we want to use the smaller error (but without the ABS on it)
            self.timingError = self.TapTime_Internal - Expected_next_DB
            quantum_of_error = Error1
         else: 
            self.timingError = self.TapTime_Internal - self.TapTime_External
            quantum_of_error = Error2
         self.timingErrorCumulative = self.timeSmoothingFactor*self.timingErrorCumulative + (1.0-self.timeSmoothingFactor)*self.timingError
         if quantum_of_error*1000 > self.muteThresh:
            self.isMuted = True
            self.checkbox3.check()
            self.Player.setMute(True)
         else:
            self.isMuted = False
            self.checkbox3.uncheck()
            self.Player.setMute(False)

   def updateEffectiveTempo(self):
      adjustment_time = self.timingErrorCumulative/16.0
      nominal_time = 60.0/(self.tempo*4)
      required_time = nominal_time-adjustment_time
      self.adjusted_16count = 60.0/required_time

   def startTimer(self):
      self.metronome()
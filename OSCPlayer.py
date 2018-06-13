###############################################################
# OSC Player class by Daniel Field                            #
# This player is adapted from the Lyrical Player.             #
# It is modified to send notes via OSC rather than using      #
# MIDI 'Part'.                                                #
#                                                             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

#from music import *  *** should not be needing the 'MUSIC' module at all in this version
from NotepoolHandler import *
from Z_CadencePlanner import *
from NoteSender import *
from random import *
from NotePicker import *
from Motif import *
from gui import *

class OSCPlayer:
   def __init__(self, ls=None):
      """Initialises an OSCPlayer object"""
      self.botName = "DF_lyrical_player_reborn"
      self.range_top = 80 # 81 = the A above middle C
      self.range_bottom = 55 # 50 = the A below middle C
      self.target_step = 2.7 # this can be varied - will affect the note choice
      self.near_top = False
      self.near_bottom = False
      self.improv_notes = [64, 65] # this was previously a Phrase object - changed to list
      self.improv_durations = [0.5, 0.5]
      self.improv_velocities = [65, 75]
      self.music = [] # this was previously a Parft object - changed to list
      self.swinging = False
      self.swing_amount = 0.5 #0.61
      self.latest_note = self.range_bottom+1
      self.thisBeatRhythm = [0.5, 0.5]
      self.thisBeatNotes = [64, 65]
      self.thisBeatVelocities = [100, 100]
      self.nextBeatRhythm = [0.5, 0.5]
      self.nextBeatNotes = [66, 67]
      self.nextBeatVelocities = [100, 100]
      self.notepool = [64, 68, 71]
      self.notepool_full_range = [64, 68, 71, 76, 80, 83, 88]
      self.chordscale = []
      for i in range(120):
         self.chordscale.append(i)
      self.incoming_chordscale = self.chordscale
      self.long_note = False
      self.play = True
      self.manually_muted = False
      self.NP = NotePicker()
      self.cp = CadencePlanner()
      self.sender = NoteSender()
      self.MM = Motif()
      self.cadence = self.cp.generateNewCadence()
      self.cadence_position = 0
      self.new_cadence_to_be_generated = False
      self.volume = 10
      self.density = 0.5
      self.current_beat = 0
      self.beat_count = 0
      self.position_count = 0
      self.legato = False
      self.isMuted = False
      self.zippiness = 0

      # GUI
      self.label1 = Label("Volume: "+str(int(self.volume))+"  ")
      self.label2 = Label("Step Size: "+str(int(self.target_step*10))+"  ")
      self.label3 = Label("Density: "+str(int(int(self.density*100)))+"  ")
      self.label4 = Label("Range Top: "+str(self.range_top)+"  ")
      self.label5 = Label("Range Btm: "+str(self.range_bottom)+"  ")
      self.d = Display("Player Parameters", 540, 480, 580, 200, Color(227, 240, 255))
      self.slider1 = Slider(HORIZONTAL, 0, 127, int(self.volume), self.setVolume)
      self.slider2 = Slider(HORIZONTAL, 0, 100, int(self.target_step*10), self.setStep)
      self.slider3 = Slider(HORIZONTAL, 0, 100, int(self.density*100), self.setDensity)
      self.slider4 = Slider(HORIZONTAL, 40, 120, int(self.range_top), self.setRangeTop)
      self.slider5 = Slider(HORIZONTAL, 0, 80, int(self.range_bottom), self.setRangeBottom)      
      self.checkbox1 = Checkbox("swing", self.setSwing)
      self.checkbox2 = Checkbox("mute", self.setMute)
      self.checkbox_legato = Checkbox("legato", self.setLegato)
      self.button1 = Button("new phrase", self.getNewCadence)
      self.ddl1 = DropDownList(["piano", "vibes", "rock organ", "distortion guitar", "warm pad", "bowed glass"], self.changeInstrument)
      self.d.add(self.label1, 40, 30)
      self.d.add(self.slider1, 40, 60)
      self.d.add(self.label2, 40, 100)
      self.d.add(self.slider2, 40, 130)
      self.d.add(self.label3, 40, 170)
      self.d.add(self.slider3, 40, 200)
      self.d.add(self.checkbox1, 270, 30)
      self.d.add(self.checkbox2, 330, 30)
      self.d.add(self.label4, 270, 100)
      self.d.add(self.slider4, 270, 130)
      self.d.add(self.label5, 270, 170)
      self.d.add(self.slider5, 270, 200)
      self.d.add(self.button1, 270, 60)
      self.d.add(self.ddl1, 40, 260)
      self.d.add(self.checkbox_legato, 270, 260)

      if ls != None:
         print "this player will ignore the lead sheet"

   def getNewCadence(self):
      self.new_cadence_to_be_generated = True

   def getNoteSender(self, note_sender):
      self.note_sender = note_sender

   def rangeLimit(self, full_series):
      return_values = []
      for element in full_series:
         if element >= self.range_bottom and element <= self.range_top:
            return_values.append(element)
      if len(return_values) == 0:
         return_values.append(self.range_bottom)
      return return_values

   def newNotepoolMessage(self, message):
      print "player received notepool message"
      self.notepool = self.nph.receiveNotepool(message)
      self.notepool_full_range = self.nph.buildFullRange(self.notepool, self.range_top, self.range_bottom)
      print str(self.notepool)
      print str(self.notepool_full_range)

   def newChordscaleMessage(self, message):
      print "player received chordscale message"
      self.incoming_chordscale = self.nph.receiveNotepool(message)
      print "received chordscale: "+str(self.incoming_chordscale)
      self.chordscale = self.nph.buildFullRange(self.incoming_chordscale, self.range_top, self.range_bottom)
      print str(self.chordscale)

   def refreshRanges(self):
      self.notepool_full_range = self.nph.buildFullRange(self.notepool, self.range_top, self.range_bottom)
      self.chordscale = self.nph.buildFullRange(self.incoming_chordscale, self.range_top, self.range_bottom)

   def playCurrentBeat(self, tempo=None): # WILL NOT WORK any more, since the self.music object has been changed to a list
      pass
      #if tempo is None: tempo = 120
      #self.music.setTempo(tempo)
      #if self.long_note == False and self.play == True and self.manually_muted == False:
      #   Play.midi(self.music)

   def beat(self, count, tempo):
      velocity = 0
      if count == 0: # this is the beginning of a bar
         self.position_count = 0
         self.beat_count = 0
      if self.beat_count == 0: # this is an 8th note onset
         if self.position_count == 0: # this is the first 8th note
            note = self.improv_notes[0]
            velocity = 56
         elif self.position_count == 3: # this is the third 8th note
            note = self.improv_notes[1]
            velocity = 65
         self.position_count += 1
         if self.position_count > 3:
            self.position_count = 0

         else:
            velocity = 0
            note = 0      
      else: # beat count is 2, which means we're on the "off" 16th
         if self.legato == False:
            velocity = 0
            note = 0
         else:
            velocity = self.lastVelocity
            note = self.lastNote
      if self.position_count == 3 or self.position_count == 7:
         pick = self.NP.pickNote(note, "A", self.chordscale)
      else:
         pick = self.NP.pickNote(note, "C", self.chordscale)
      if self.isMuted is True:
         velocity = 0
      self.sender.sendNoteEvent(pick, velocity, self.zippiness, self.botName)
      self.lastNote = pick
      self.lastVelocity = velocity
      self.beat_count += 1
      if self.beat_count > 1:
         self.beat_count = 0
      if count%4 == 0:
         self.beat_no = count/4 + 1
         print self.beat_no
         self.teeUpNextBeat()



   def teeUpNextBeat(self):
      l1, l2, l3, l4, n1, n2, n3, n4 = self.planNextBeat()
      #c, a, d, b = self.pickNextBeatNotes()
      c, a, d, b = self.range_bottom, self.swing_amount, self.range_bottom+4, 1.0-self.swing_amount
      e = self.volume + int(randint(-10, 10)*0.01*self.volume)
      f = e + int(randint(-20, 5)*0.01*self.volume)
      if e < 0: e = 0
      if e > 127: e = 127
      if f < 0: f = 0
      if f > 127: f=127
      self.nextBeatRhythm = [l1, l2, l3, l4]
      self.nextBeatNotes = [n1, n2, n3, n4]
      self.nextBeatVelocities = [e, f, e, f]
      self.improv_notes = []
      self.improv_durations = []
      self.improv_velocities = []
      self.music = []
      self.thisBeatRhythm = self.nextBeatRhythm
      self.thisBeatNotes = self.nextBeatNotes
      self.thisBeatVelocities = self.nextBeatVelocities
      for note in self.thisBeatNotes:
         self.improv_notes.append(note)
      print self.improv_notes
      #self.improv_notes.append(self.thisBeatNotes)
      for duration in self.thisBeatRhythm:
         self.improv_durations.append(duration)
      #self.improv_durations.append(self.thisBeatRhythm)
      for velocity in self.thisBeatVelocities:
         self.improv_velocities.append(velocity)
      #self.improv_velocities.append(self.thisBeatVelocities)
      #self.improv.addNoteList(self.thisBeatNotes, self.thisBeatRhythm, self.thisBeatVelocities)
      #self.music.addPhrase(self.improv)

   def planNextBeat(self):
      if self.swinging == True:
         l1, l2, l3, l4 = self.swing_amount*0.5, self.swing_amount*0.5, 1.0-self.swing_amount, 0.0
      else:
         l1, l2, l3, l4 = 0.25, 0.25, 0.25, 0.25
      n1, n2, n3, n4 = 0, 0, 0, 0
      headroom = float(self.range_top - self.latest_note)
      footroom = float(self.latest_note - self.range_bottom)
      rangeroom = float(self.range_top - self.range_bottom)
      local_target_step = self.target_step # just in case someone changes the value on the fly
      target_notes = []
      actual_notes = []
      if self.current_beat == 1 or self.current_beat == 3:
         # next beat is a weak beat, want to get to the next 'S' on it
         # count how many syllables need to be fit in
         syllables = 0
         while self.cadence[self.cadence_position] != "S" and self.cadence_position < len(self.cadence)-1:
            syllables += 1
            self.cadence_position += 1
         # reset to start if it's reached the end
         if self.cadence_position == len(self.cadence)-1 or self.cadence_position > len(self.cadence)-1:
            self.cadence_position = 0
         # check if there are any notes to play at all
         if syllables != 0:
            # check if there's enough headroom to just go up (including space for the next strong beat)
            if headroom > (syllables+1.0)*local_target_step:
               for i in range(syllables): # this counts from zero to syllables-1
                  target_notes.append(self.latest_note+(local_target_step*(i+1)))
                  if i == syllables-1:
                     self.latest_note = target_notes[-1]
            # check if there's enough range to go up, by dropping to the first note
            elif rangeroom > (syllables+1.0)*local_target_step:
               loose_note1 = float(self.range_top)-(syllables+1.0)*local_target_step
               for i in range(syllables):
                  target_notes.append(loose_note1+(local_target_step*(i+1)))
                  if i == syllables-1:
                     self.latest_note = target_notes[-1]
            # if we've passed both the options above then the overall range of the instrument is not great enough
            # in relation to the desired step size and the number of steps. So let's arpeggio up from the bottom
            # of the range, increasing note spacing as we go.
            else:
               target_notes.append(float(self.range_bottom)) # first note should be the lowest possible
               if syllables == 2:
                  target_notes.append(float(self.range_bottom)+0.33*rangeroom)
               elif syllables == 3:
                  target_notes.append(float(self.range_bottom)+0.25*rangeroom)
                  target_notes.append(float(self.range_bottom)+0.58*rangeroom)
               elif syllables == 4:
                  target_notes.append(float(self.range_bottom)+0.2*rangeroom)
                  target_notes.append(float(self.range_bottom)+0.45*rangeroom)
                  target_notes.append(float(self.range_bottom)+0.78*rangeroom)
               elif syllables == 5:
                  target_notes.append(float(self.range_bottom)+0.13*rangeroom)
                  target_notes.append(float(self.range_bottom)+0.29*rangeroom)
                  target_notes.append(float(self.range_bottom)+0.49*rangeroom)
                  target_notes.append(float(self.range_bottom)+0.74*rangeroom)
            # That should cover every case of the off beat
            # Now map the loose target notes to exact notes
            for i in range(len(target_notes)):
               # pick the nearest scale note
               ##differences = [abs(target_notes[i] - float(note)) for note in self.chordscale]
               # find the closest
               ##closest = differences.index(min(differences))
               ##actual_notes.append(self.chordscale[closest])
               # CHANGED to get rid of the quantisation at this point
               actual_notes.append(int(target_notes[i]))
            print "actual notes (1) = "+actual_notes
         # by the time we get down to here, we should have a list of actual notes to be played.
         # Now we need to match them to the appropriate beats that were set up the top
         # NOTE this set is for the OFF beat
         if syllables != 0:
            if self.swinging == True:
               if syllables == 1:
                  choice = self.weightedChoice([1.0, 0.5, 2.0])
                  if choice == 0:
                     n1 = actual_notes[0]
                  elif choice == 1:
                     n2 = actual_notes[0]
                  elif choice == 2:
                     n3 = actual_notes[0]
               elif syllables == 2:
                  choice = self.weightedChoice([1.0, 1.0, 1.8])
                  if choice == 0:
                     n2 = actual_notes[0]
                     n3 = actual_notes[1]
                  elif choice == 1:
                     n1 = actual_notes[0]
                     n3 = actual_notes[1]
                  elif choice == 2:
                     n1 = actual_notes[0]
                     n2 = actual_notes[1]
               else:
                  n1 = actual_notes[0]
                  n2 = actual_notes[1]
                  n3 = actual_notes[2]
            else:
               if syllables == 1:
                  choice = self.weightedChoice([1.0, 0.5, 2.0, 0.5])
                  if choice == 0:
                     n1 = actual_notes[0]
                  elif choice == 1:
                     n2 = actual_notes[0]
                  elif choice == 2:
                     n3 = actual_notes[0]
                  elif choice == 3:
                     n4 = actual_notes[0]
               elif syllables == 2:
                  choice = self.weightedChoice([0.2, 1.0, 1.0, 1.0, 1.0, 1.0])
                  if choice == 0:
                     n1 = actual_notes[0]
                     n2 = actual_notes[1]
                  elif choice == 1:
                     n1 = actual_notes[0]
                     n3 = actual_notes[1]
                  elif choice == 2:
                     n1 = actual_notes[0]
                     n4 = actual_notes[1]
                  elif choice == 3:
                     n2 = actual_notes[0]
                     n3 = actual_notes[1]
                  elif choice == 4:
                     n2 = actual_notes[0]
                     n4 = actual_notes[1]
                  elif choice == 5:
                     n3 = actual_notes[0]
                     n4 = actual_notes[1]
               elif syllables == 3:
                  choice = self.weightedChoice([0.5, 1.5, 1.2, 0.5])
                  if choice == 0:
                     n2 = actual_notes[0]
                     n3 = actual_notes[1]
                     n4 = actual_notes[2]
                  elif choice == 1:
                     n1 = actual_notes[0]
                     n3 = actual_notes[1]
                     n4 = actual_notes[2]
                  elif choice == 2:
                     n1 = actual_notes[0]
                     n2 = actual_notes[1]
                     n4 = actual_notes[2]
                  elif choice == 3:
                     n2 = actual_notes[0]
                     n3 = actual_notes[1]
                     n4 = actual_notes[2]
               else:
                  n1 = actual_notes[0]
                  n2 = actual_notes[1]
                  n3 = actual_notes[2]
                  n4 = actual_notes[3]
      else: # we are planning beat 1 or 3
         # next beat is a strong beat, want to play an 'S' which is usually the first 
         # syllable (but might not be - e.g. at start of new phrase - in which case we'll
         # let it slip through to the next beat, i.e. play nothing)
         # We already know there won't be too many W's in a row so we can freely choose to play
         # no W's or the next few if desired.
         # check if the first syllable is strong
         print "next pos: "+str(self.cadence_position)
         if self.cadence[self.cadence_position] == "S":
            to_play = 1
            # check if there's at least one W following the S
            if self.cadence_position < len(self.cadence)-1:
               if self.cadence[self.cadence_position+1] != "S":
                  # we can arbitrarily choose to play one or two beats
                  choice = self.weightedChoice([1.0, 2.0])
                  if choice == 1:
                     to_play = 2
            # Now go ahead and pick the strong note
            # check if there's enough headroom to just go up
            if headroom >= local_target_step:
               target_notes.append(self.latest_note+local_target_step)
            # otherwise we'll have to play the top range note
            else:
               target_notes.append(self.range_top)
            # update the position index
            print "pos: "+str(self.cadence_position)+"   len: "+str(len(self.cadence)-1)
            if self.cadence_position < len(self.cadence)-1:
               self.cadence_position += 1
            else: self.cadence_position = 0
            # now pick a second note if we're going to play one
            if to_play == 2:
               # we're going to pick a Weak note
               # let's drop down a bit or maybe choose a random note
               choice = self.weightedChoice([1.0, 1.6, 1.1])
               if choice == 1:
                  target_notes.append(target_notes[-1]-(2*self.target_step))
               elif choice == 2:
                  target_notes.append(target_notes[-1]-(3*self.target_step))
               else:
                  target_notes.append(randrange(self.range_bottom, self.range_top, 1))
            # update the position index
            if self.cadence_position < len(self.cadence)-1:
               self.cadence_position += 1
            else: self.cadence_position = 0
            # now update the latest note variable
            self.latest_note = target_notes[-1]
         # Now map the loose target notes to exact notes
         for i in range(len(target_notes)):
            # pick the nearest scale note
            ##differences = [abs(target_notes[i] - float(note)) for note in self.notepool_full_range]
            # find the closest
            ##closest = differences.index(min(differences))
            ##actual_notes.append(self.notepool_full_range[closest])
            # CHANGED to leave just the loose target notes
            actual_notes.append(int(target_notes[i]))
         print "actual notes (2) = "+str(actual_notes)
         # by the time we get down to here, we should have a list of actual notes to be played.
         # Now we need to match them to the appropriate beats that were set up the top
         # NOTE this set is for the ON beat (S or SW)
         if self.swinging == True:
            if len(actual_notes) == 1:
               n1 = actual_notes[0]
               l1 = 0.95
               l2 = 0.0
               l3 = 0.0
               l4 = 0.0
            elif len(actual_notes) == 2:
               n1 = actual_notes[0]
               n2 = actual_notes[1]
               choice = self.weightedChoice([5.0, 1.0])
               if choice == 0:
                  l1 = self.swing_amount
                  l2 = 1.0 - self.swing_amount
                  l3 = 0.0
         else:
            if len(actual_notes) == 1:
               n1 = actual_notes[0]
               l1 = 0.95
               l2 = 0.0
               l3 = 0.0
               l4 = 0.0
            elif len(actual_notes) == 2:
               n1 = actual_notes[0]
               n2 = actual_notes[1]
               choice = self.weightedChoice([3.0, 1.0])
               if choice == 0:
                  l1 = 0.5
                  l2 = 0.45
                  l3 = 0.0
                  l4 = 0.0
               else:
                  l1 = 0.75
                  l2 = 0.2
                  l3 = 0.0
                  l4 = 0.0

      if self.new_cadence_to_be_generated == True:
         self.cadence = self.cp.generateNewCadence()
         self.cadence_position = 0
         self.new_cadence_to_be_generated = False

      return l1, l2, l3, l4, n1, n2, n3, n4



   def pickNextBeatNotes(self):
      last_note = self.thisBeatNotes[-1]
      second_last_note = self.thisBeatNotes[-2]
      # work out if the last direction was up, default to YES is unsure
      a = self.swing_amount
      b = 1.0 - a
      direction_up = True
      if last_note != REST and second_last_note != REST:
         if second_last_note - last_note > 0:
            direction_up = False
      # develop a loose target note
      if direction_up == False:
         loose_target = float(last_note) - self.target_step
      else:
         loose_target = float(last_note) + self.target_step
      # want to start with a "chord note"
      # check how far the potential notes are from the loose target
      differences = [abs(loose_target - float(note)) for note in self.notepool_full_range]
      # find the closest, and select it as the first note
      closest = differences.index(min(differences))
      # check if near top or bottom (i.e. used first or last element in 37 list)
      if closest == 0:
         self.near_bottom = True
      elif closest == len(self.notepool_full_range)-1:
         self.near_top = True
      else:
         self.near_bottom = False
         self.near_top = False
      first_note = self.notepool_full_range[closest]
      # now it's time to pick a second note
      # if we're near range top we'll go down, and vice versa
      if self.near_bottom:
         loose_target = float(first_note) + self.target_step
      elif self.near_top:
         loose_target = float(first_note) - (2*self.target_step)
      else:
         loose_target = choice([float(first_note) + self.target_step, float(first_note) - self.target_step])
      # now pick the nearest scale note as above
      differences = [abs(loose_target - float(note)) for note in self.chordscale]
      # find the closest, and select it as the second note
      closest = differences.index(min(differences))
      second_note = self.chordscale[closest]
      if self.density < 0.25:
         return first_note, 1.0, second_note, 0.0
      elif self.density > 0.75:
         return first_note, a*0.5, second_note, b*0.5
      else:
         return first_note, a, second_note, b
      
   #def beat(self, beat_no, tempo=None):
   #   self.playCurrentBeat(tempo)
   #   beat_no += 1
   #   if beat_no > 4: beat_no = 1
   #   self.current_beat = beat_no
   #   print "current beat = "+str(self.current_beat)
   #   self.teeUpNextBeat()

   def mute(self):
      self.play = False
      print "Player MUTE command received"

   def unmute(self):
      self.play = True

   def setVolume(self, newVolume):
      self.volume = int(newVolume)
      self.label1.setText("Volume: "+str(newVolume))

   def setStep(self, newStep):
      self.target_step = float(newStep)/10.0
      self.label2.setText("Step Size: "+str(newStep))

   def setDensity(self, newDensity):
      self.density = float(newDensity)/100.0
      self.label3.setText("Density: "+str(newDensity))

   def setSwing(self, newSwing):
      if newSwing == True:
         self.swing_amount = 0.61
         self.swinging = True
      elif newSwing == False:
         self.swing_amount = 0.5
         self.swinging = False

   def setRangeTop(self, new_range_top):
      if new_range_top > self.range_bottom:
         self.range_top = int(new_range_top)
         self.label4.setText("Range Top: "+str(new_range_top))
         self.refreshRanges()

   def setRangeBottom(self, new_range_bottom):
      if new_range_bottom < self.range_top:
         self.range_bottom = int(new_range_bottom)
         self.label5.setText("Range Btm: "+str(new_range_bottom))
         self.refreshRanges()

   def setMute(self, new_mute):
      if new_mute == True:
         self.manually_muted = True
      elif new_mute == False:
         self.manually_muted = False

   def changeInstrument(self, newInstrument):
      # "piano", "vibes", "rock organ", "distortion guitar", "warm pad", "bowed glass"
      if newInstrument == "piano":
         self.music.setInstrument(1)
      elif newInstrument == "vibes":
         self.music.setInstrument(11)
      elif newInstrument == "rock organ":
         self.music.setInstrument(18)
      elif newInstrument == "distortion guitar":
         self.music.setInstrument(30)
      elif newInstrument == "warm pad":
         self.music.setInstrument(89)
      elif newInstrument == "bowed glass":
         self.music.setInstrument(92)

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

   def sendAlive(self):
      self.sender.sendAlive(self.botName)

   def newChordscale(self, newChordscale):
      self.chordscale = self.NP.buildFullRange(newChordscale)

   def setLegato(self, newLegato):
      self.legato = newLegato



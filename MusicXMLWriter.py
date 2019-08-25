####################################################################
# Music XML Writer class by Daniel Field                           #
#                                                                  #
# This class handles the creation and appending of a MusicXML file #
#                                                                  #
# check out www.github.com/dan-field/jazz for info and rights      #
####################################################################

class MusicXMLWriter:
   def __init__(self, usrTitle=None, progID=None):
      """Initialises a MusicXMLWriter object"""
      if usrTitle is None:
         self.Title = "Parametric Melody"
      else:
         self.Title = str(usrTitle)
      if progID is None:
         self.progID = "CompAssist v0.20"
      else:
         self.progID = str(progID)
      self.DIVISIONS = 12 # number of counts per crotchet
      self.ticksPerBar = 48
      self.measureNo = 0
      self.tie_active = False # flag to indicate that a tie has been opened but not closed
      self.tied_note = -1 # MIDI number of note being tied over (initialised to -1 for 'rest')
      self.voice = 1 # 1 Soprano, 2 Alto, 3 Tenor, 4 Bass
      self.flats = True # assumes black notes should be written as flats - will need to be updated once a 'key' functionality is added
      self.file = None
      self.fileName = ""
      self.MIDI_by_bar = []
      self.Tick_by_bar = []

   def writeMelodyFromTickList(self, key, MIDIList, TickList, BarList, ticksPerBar):
      totalBars = BarList[-1] # last entry in the BarList shows the total number of bars
      MIDI_by_bar = []
      Tick_by_bar = []
      for bar in range(totalBars):
         thisBarMIDINos = []
         thisBarTicks = []
         for index in range(len(MIDIList)):
            if BarList[index] == bar:
               thisBarMIDINos.append(MIDIList[index])
               thisBarTicks.append(TickList[index])
               self.ticksPerBar = ticksPerBar[index]
         MIDI_by_bar.append(thisBarMIDINos)
         Tick_by_bar.append(thisBarTicks)
      # now we have three lists of lists, representing the bars
      print "MIDI numbers by bar: "+str(MIDI_by_bar)
      print "Tick numbers by bar: "+str(Tick_by_bar)
      self.startFile()
      self.startPart()
      tiedOver = False
      tiedMIDI = -1
      for b, bar in enumerate(Tick_by_bar): # go through the bars one at a time
         if b > 0: # skip over the first bar (dud bar)
            if len(bar) == 0: # it's an empty bar
               if tiedOver is True:
                  self.addNote(tiedMIDI, self.ticksPerBar) # put in a tied minim
                  self.addMeasure()
                  tiedOver = False # don't want to tie over more than one extra bar
               else:
                  self.addNote(-1, self.ticksPerBar) # add a whole bar rest
                  self.addMeasure()
            else: # the bar is not empty
               noteLengths = []
               previousOnset = 0
               for note in bar: # actually note onsets by Tick number
                  noteLengths.append(note-previousOnset) # note: first value in each bar is the Ticks BEFORE the first note (may be 0)
                  previousOnset = note
               noteLengths.append(self.ticksPerBar-previousOnset) # add on the final duration to the end of the bar
               print "note lengths in bar "+str(b)+": "+str(noteLengths) # Ticks to first note, then durations of subsequent notes
               for n, noteLength in enumerate(noteLengths): # go through the bar that's just been constructed
                  if n == 0: # this is the first value (i.e. ticks BEFORE first note)
                     if noteLength > 0: # we must have a tied over note
                        self.addNote(tiedMIDI, noteLength, "stop")
                  else:
                     thisNote = MIDI_by_bar[b][n-1]
                     if n == len(noteLengths)-1: # this is the last note in the bar
                        if len(Tick_by_bar) > b+1: # there's at least one more bar to go
                           if len(Tick_by_bar[b+1]) > 0: # there's at least one note in the next bar
                              if Tick_by_bar[b+1][0] > 0: # the next bar's first note is tied over from this bar
                                 self.addNote(thisNote, noteLength, "start")
                                 tiedMIDI = thisNote
                              else:
                                 self.addNote(thisNote, noteLength)
                           else:
                              self.addNote(thisNote, noteLength)
                        else:
                           self.addNote(thisNote, noteLength)
                     else:
                        self.addNote(thisNote, noteLength)
               self.addMeasure()
      self.endPart()
      self.endFile()


   def startFile(self):
      usrFileName = raw_input("please enter a name for the output file\n: ")
      self.fileName = usrFileName+".musicxml"
      try:
         self.file = open(self.fileName, "w")
      except (OSError, IOError):
         self.file = None
         print "\nThere was an issue with the file operation."
         print "Please double-check your filename.\n"
         print "Note the MusicXML file will attempt to save in the"
         print "same folder as the Python files; please ensure you"
         print "have write permission for that folder."
         return
      self.file.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
      self.file.write('<!DOCTYPE score-partwise PUBLIC\n')
      self.file.write('     "-//Recordare//DTD MusicXML 3.1 Partwise//EN"\n')
      self.file.write('     "http://www.musicxml.org/dtds/partwise.dtd">\n')
      self.file.write('<score-partwise version="3.1">\n')
      self.file.write('  <work>\n')
      self.file.write('    <work-title>'+str(self.Title)+'</work-title>\n')
      self.file.write('  </work>\n')
      self.file.write('  <identification>\n')
      self.file.write('    <creator type="composer">'+str(self.progID)+'</creator>\n')
      self.file.write('  </identification>\n')
      self.file.write('  <part-list>\n')
      self.file.write('    <score-part id="P1">\n')
      self.file.write('      <part-name>melody</part-name>\n')
      self.file.write('    </score-part>\n')
      self.file.write('  </part-list>\n')

   def startPart(self, key=None):
      if self.file is not None:
         self.measureNo = 0
         self.voice = 1
         if key is None:
            key = -1
         self.file.write('  <part id="P1">\n')
         self.file.write('    <measure number="'+str(self.measureNo)+'">\n')
         #self.file.write('      <text>\n')
         #self.file.write('        <tempo>1.33333</tempo>\n')
         #self.file.write('        <followText>1</followText>\n')
         #self.file.write('        <text><sym>unicodeNoteQuarterUp</sym> = 80</text>\n')
         #self.file.write('      </text>\n')
         self.file.write('      <attributes>\n')
         self.file.write('        <divisions>'+str(self.DIVISIONS)+'</divisions>\n')
         self.file.write('        <key>\n')
         self.file.write('          <fifths>'+str(key)+'</fifths>\n')
         self.file.write('        </key>\n')
         self.file.write('        <time>\n')
         self.file.write('          <beats>4</beats>\n')
         self.file.write('          <beat-type>4</beat-type>\n')
         self.file.write('        </time>\n')
         self.file.write('        <clef number="1">\n')
         self.file.write('          <sign>G</sign>\n')
         self.file.write('          <line>2</line>\n')
         self.file.write('        </clef>\n')
         self.file.write('      </attributes>\n')

   def endPart(self):
      if self.file is not None:
         #self.file.write('      </note>\n')
         self.file.write('      <barline location="right">\n')
         self.file.write('        <bar-style>light-heavy</bar-style>\n')
         self.file.write('      </barline>\n')
         self.file.write('    </measure>\n')
         self.file.write('  </part>\n')

   def endFile(self):
      if self.file is not None:
         self.file.write('</score-partwise>\n')
         self.file.close()

   def addMeasure(self):
      if self.file is not None:
         self.file.write('    </measure>\n')
         self.measureNo += 1
         self.file.write('    <measure number="'+str(self.measureNo)+'">\n')

   def addMeasureDbl(self):
      if self.file is not None:
         self.file.write('    </measure>\n')
         self.measureNo += 1
         self.file.write('    <measure number="'+str(self.measureNo)+'">\n')
         self.file.write('      <barline location="left">\n')
         self.file.write('        <bar-style>light-light</bar-style>\n')
         self.file.write('      </barline>\n')

   def addMeasureKeyChange(self, newKey):
      if self.file is not None:
         self.file.write('    </measure>\n')
         self.measureNo += 1
         self.file.write('    <measure number="'+str(self.measureNo)+'">\n')
         self.file.write('      <barline location="left">\n')
         self.file.write('        <bar-style>light-light</bar-style>\n')
         self.file.write('      </barline>\n')
         self.file.write('      <attributes>\n')
         self.file.write('        <key>\n')
         self.file.write('          <fifths>'+str(newKey)+'</fifths>\n')
         self.file.write('        </key>\n')
         self.file.write('      </attributes>\n')

   def addNote(self, MIDI_No, duration=None, tie=None): # duration: 12 = crotchet, 48 = semi-breve
      if self.file is not None:
         if duration is None:
            duration = 12 # default to a crotchet
         note_type, dotted, tiedToMinim = self.Duration2Type(duration)
         self.file.write('      <note>\n')
         if MIDI_No != -1:
            octave, step, alter = self.MIDI2Note(MIDI_No, self.flats)
            self.file.write('        <pitch>\n')
            self.file.write('          <step>'+str(step)+'</step>\n')
            if alter != 0:
               self.file.write('          <alter>'+str(alter)+'</alter>\n')
            self.file.write('          <octave>'+str(octave)+'</octave>\n')
            self.file.write('        </pitch>\n')
         else:
            self.file.write('        <rest/>\n')
         if tiedToMinim is False:
            self.file.write('        <duration>'+str(duration)+'</duration>\n')
         else:
            self.file.write('        <duration>'+str(duration-24)+'</duration>\n')
         self.file.write('        <voice>'+str(self.voice)+'</voice>\n')
         self.file.write('        <type>'+str(note_type)+'</type>\n')
         if dotted is True:
            self.file.write('        <dot></dot>\n')
         if tie is not None and tiedToMinim is False:
            self.file.write('        <notations>\n')
            self.file.write('          <tied type="'+str(tie)+'"></tied>\n')
            self.file.write('        </notations>\n')
         if tiedToMinim is True:
            self.file.write('        <notations>\n')
            if tie == "stop":
               self.file.write('          <tied type="stop"></tied>\n')
            self.file.write('          <tied type="start"></tied>\n')
            self.file.write('        </notations>\n')            
         self.file.write('      </note>\n')
         if tiedToMinim is True:
            self.file.write('      <note>\n')
            if MIDI_No != -1:
               self.file.write('        <pitch>\n')
               self.file.write('          <step>'+str(step)+'</step>\n')
               if alter != 0:
                  self.file.write('          <alter>'+str(alter)+'</alter>\n')
               self.file.write('          <octave>'+str(octave)+'</octave>\n')
               self.file.write('        </pitch>\n')
            else:
               self.file.write('        <rest/>\n')
            self.file.write('        <duration>24</duration>\n')
            self.file.write('        <voice>'+str(self.voice)+'</voice>\n')
            self.file.write('        <type>half</type>\n')
            self.file.write('        <notations>\n')
            self.file.write('          <tied type="stop"></tied>\n')
            if tie == "start":
               self.file.write('          <tied type="start"></tied>\n')
            self.file.write('        </notations>\n')
            self.file.write('      </note>\n')

   def addNoteMayBeTied(self, MIDI_No, duration=None, tie=None): # copy of addNote() except the last couple of lines are left off
      if self.file is not None:
         if duration is None:
            duration = 12 # default to a crotchet
         note_type, dotted, tiedToMinim = self.Duration2Type(duration)
         self.file.write('      <note>\n')
         if MIDI_No != -1:
            octave, step, alter = self.MIDI2Note(MIDI_No, self.flats)
            self.file.write('        <pitch>\n')
            self.file.write('          <step>'+str(step)+'</step>\n')
            if alter != 0:
               self.file.write('          <alter>'+str(alter)+'</alter>\n')
            self.file.write('          <octave>'+str(octave)+'</octave>\n')
            self.file.write('        </pitch>\n')
         else:
            self.file.write('        <rest/>\n')
         self.file.write('        <duration>'+str(duration)+'</duration>\n')
         self.file.write('        <voice>'+str(self.voice)+'</voice>\n')
         self.file.write('        <type>'+str(note_type)+'</type>\n')
         if dotted is True:
            self.file.write('        <dot></dot>\n')
         if tie is not None:
            self.file.write('        <notations>\n')
            self.file.write('          <tied type="'+str(tie)+'"></tied>\n')
            self.file.write('        </notations>\n')

   def closeNoteWithTieStart(self):
      if self.file is not None:
         self.file.write('        <notations>\n')
         self.file.write('          <tied type="start"></tied>\n')
         self.file.write('        </notations>\n')
         self.file.write('      </note>\n')

   def closeNoteWithoutTieStart(self):
      if self.file is not None:
         self.file.write('      </note>\n')

   def addFirstBarOfNotes(self, noteList, timingList): # same as below except it doesn't close off the previous note (since there is no previous note)
      first_note_completes_tie = False
      durations_list = []
      time_previous = 0
      for i, time in enumerate(timingList): # go through the list of onset times
         if time != 0: # at each onset, we're counting the duration of the PREVIOUS note, so we ignore any onset at time zero (previous note already closed off in previous bar)
            if i == 0: # it's first onset but time is NOT zero: that means the previous bar's last note (or rest) is carried over
               noteList.insert(0, self.tied_note) # we need to add the tied over note to the start of the note list
               if self.tied_note != -1: # the previous bar ended with a note (not a rest)
                  first_note_completes_tie = True # update
            durations_list.append(time - time_previous) # this is the duration of the note prior to this onset (looking back no further than the start of the bar)
            time_previous = time # this note's onset becomes the new reference for calculating the next duration
         if sum(durations_list) < 48:
            durations_list.append(48 - time_previous) # time from last onset to end of bar
      for i, duration in enumerate(durations_list): # go through the list of durations
         if i == 0: # this is the first note of the bar
            self.addNoteMayBeTied(noteList[i], duration) # write the notes into the XML file without ending tie
         else: # this is not the first note of this bar
            self.closeNoteWithoutTieStart()
            self.addNoteMayBeTied(noteList[i], duration)
      self.tied_note = noteList[-1] # update the 'tied note' MIDI number to match the last note of this bar, in case it is needed next bar

   def addBarOfNotes(self, noteList, timingList): # list of MIDI numbers and onset reference times
      first_note_completes_tie = False
      durations_list = []
      time_previous = 0
      for i, time in enumerate(timingList): # go through the list of onset times
         if time != 0: # at each onset, we're counting the duration of the PREVIOUS note, so we ignore any onset at time zero (previous note already closed off in previous bar)
            if i == 0: # it's first onset but time is NOT zero: that means the previous bar's last note (or rest) is carried over
               noteList.insert(0, self.tied_note) # we need to add the tied over note to the start of the note list
               if self.tied_note != -1: # the previous bar ended with a note (not a rest)
                  first_note_completes_tie = True # update
            durations_list.append(time - time_previous) # this is the duration of the note prior to this onset (looking back no further than the start of the bar)
            time_previous = time # this note's onset becomes the new reference for calculating the next duration
         if sum(durations_list) < 48:
            durations_list.append(48 - time_previous) # time from last onset to end of bar
      for i, duration in enumerate(durations_list): # go through the list of durations
         if i == 0: # this is the first note of the bar
            if first_note_completes_tie:
               self.closeNoteWithTieStart()
               self.addMeasure()
               self.addNoteMayBeTied(noteList[i], duration, "stop") # write the notes into the XML file with ending tie
            else:
               self.closeNoteWithoutTieStart()
               self.addMeasure()
               self.addNoteMayBeTied(noteList[i], duration) # write the notes into the XML file without ending tie
         else: # this is not the first note of this bar
            self.closeNoteWithoutTieStart()
            self.addNoteMayBeTied(noteList[i], duration)
      if len(noteList) > 0:
         self.tied_note = noteList[-1] # update the 'tied note' MIDI number to match the last note of this bar, in case it is needed next bar
      else:
         self.tied_note = -1 # if the noteList is empty, set 'tied note' back to 'rest'

   def backOneBar(self):
      if self.file is not None:
         self.file.write('      <backup>\n')
         self.file.write('        <duration>'+str(int(self.DIVISIONS*4))+'</duration>\n') # assuming 4 beats per bar
         self.file.write('      </backup>\n')

   def writeMelody(self, key, notes, durations, ties=None):
      self.startPart(key)
      for Vindex, verse in enumerate(notes):
         for Bindex, bar in enumerate(verse):
            if Bindex == len(verse)-1 and Vindex != len(notes)-1: # it's the last bar of the verse but not the last verse
               self.addMeasureDbl()
            elif Bindex == len(verse)-1 and Vindex == len(notes)-1: # this is the very last bar; don't add a new bar
               #pass
               self.addMeasure()
            elif Bindex != 0:
               self.addMeasure()
            for Nindex, note in enumerate(bar):
               self.addNote(bar[Nindex], durations[Vindex][Bindex][Nindex])
      self.endPart()

   def MIDI2Fifths(self, MIDI_Key):
      MIDI_Key = int(MIDI_Key)
      MIDI_Key = MIDI_Key%12
      if MIDI_Key == 1: # D flat
         fifths = -5
      elif MIDI_Key == 2: # D
         fifths = 2
      elif MIDI_Key == 3: # E flat
         fifths = -3
      elif MIDI_Key == 4: # E
         fifths = 4
      elif MIDI_Key == 5: # F
         fifths = -1
      elif MIDI_Key == 6: # F sharp
         fifths = 6
      elif MIDI_Key == 7: # G
         fifths = 1
      elif MIDI_Key == 8: # A flat
         fifths = -4
      elif MIDI_Key == 9: # A
         fifths = 3
      elif MIDI_Key == 10: # B flat
         fifths = -2
      elif MIDI_Key == 11: # B
         fifths = 5
      else:
         fifths = 0
      return fifths

   def MIDI2Note(self, MIDI_No, flats=None):
      # this function converts a MIDI number into a note and octave
      # 'flats' means to notate 'black notes' as flats; if flats is False then they'll be notated as sharps
      if flats is None:
         flats = True
      octave = (int(MIDI_No)/12)-1 # based on MIDI note 'zero' being in octave '-1'
      note = int(MIDI_No)%12 # MIDI note 'zero' is a C
      alter = 0 # this is the individual note's sharp/flat designation in MusicXML
      if note == 0:
         step = "C"
      elif note == 1:
         if flats is True:
            step = "D"
            alter = -1
         else:
            step = "C"
            alter = 1
      elif note == 2:
         step = "D"
      elif note == 3:
         if flats is True:
            step = "E"
            alter = -1
         else:
            step = "D"
            alter = 1
      elif note == 4:
         step = "E"
      elif note == 5:
         step = "F"
      elif note == 6:
         if flats is True:
            step = "G"
            alter = -1
         else:
            step = "F"
            alter = 1
      elif note == 7:
         step = "G"
      elif note == 8:
         if flats is True:
            step = "A"
            alter = -1
         else:
            step = "G"
            alter = 1
      elif note == 9:
         step = "A"
      elif note == 10:
         if flats is True:
            step = "B"
            alter = -1
         else:
            step = "A"
            alter = 1
      elif note == 11:
         step = "B"
      return octave, step, alter

   def Duration2Type(self, duration):
      # this function converts a duration value to a note type
      # it assumes 12 = crotchet, 48 = semi-breve (that is, "divisions" is equal to 12)
      dotted = False
      tiedToMinim = False
      if duration == 3:
         Ntype = "16th"
      elif duration == 6:
         Ntype = "eighth"
      elif duration == 9:
         Ntype = "eighth"
         dotted = True
      elif duration == 12:
         Ntype = "quarter"
      elif duration == 18:
         Ntype = "quarter"
         dotted = True
      elif duration == 24:
         Ntype = "half"
      elif duration == 30:
         Ntype = "eighth"
         tiedToMinim = True
      elif duration == 36:
         Ntype = "half"
         dotted = True
      elif duration == 42:
         Ntype = "quarter"
         dotted = True
         tiedToMinim = True
      elif duration == 48:
         Ntype = "whole"
      else:
         Ntype = "quarter"
      return Ntype, dotted, tiedToMinim


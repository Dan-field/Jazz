###############################################################
# Harmonic Structure class by Daniel Field                    #
# derived from earlier 'LeadSheet' class                      #
# contains functions to be used in the improvisor             #
# check out www.github.com/dan-field/jazz for info and rights #
###############################################################

# This class is intended to perform the functions described as
# 'harmonic structure', namely:
# - to read in a chord chart and perform key analysis on it
# - to read in a chord+key chart (without performing key analysis)
# - to provide a means for direct entry of chord/key or notepools
# - to provide an OSC pipe for notepools

from string import *
from gui import *
from guicontrols import *

class HarmonicStructure:
   def __init__(self, textFile=None):
      """Initialises a HarmonicStructure object"""
      # set up the class variables
      self.UL = None # placeholder for Urline reference
      self.PP = None # placeholder for Player reference
      self.defaultBeatsPerBar = 4 # used if the text file has no timesig
      self.ticksPerBar = 48
      self.thisTick = 0
      self.thisBeat = 0
      self.thisBar = 0
      self.tickTimer = Timer(0, self.TickInternal, [], False)
      self.chordBases = [] # for the chord base's MIDI number
      self.chordTypes = [] # to be one of 'Maj', 'min', 'Dom', 'dim', 'mb5' (note: mb5 is 'half diminished')
      self.chordExtns = [] # any leftover information from the chord symbol
      self.keyBases0 = [] # the key's MIDI number for the key read from the text file
      self.keyBases1 = [] # the key's MIDI number for option 1: single key as analysed
      self.keyBases2 = [] # the key's MIDI number for option 2: analysed key with ii-V modulations
      self.keyBases3 = [] # the key's MIDI number for option 3: analysed key with ii-V-I modulations
      self.keyBases4 = [] # the key's MIDI number for option 4: analysed key with ii-V and ii-V-I modulations
      self.keyTypes0 = [] # 'Maj' or 'min' for the key read from the text file
      self.keyTypes1 = [] # 'Maj' or 'min' for options 1 and 2
      self.keyTypes2 = [] # 'Maj' or 'min' for options 3 and 4
      self.I_singleKey = [] # locations of 'I' chords in the analysed single key
      self.keyBaseManual = -1
      self.keyTypeManual = ""
      self.thisKeyBase = -1
      self.thisKeyType = ""
      self.keyMode = 0 # 0 = no key, 1 = manual, 2 = from file, 3 = analysis0, 4 = analysis1, 5 = analysis2, 6 = analysis3
      # set up the array of scale choices for major and minor keys: top level lists correspond to the root positions 0-11
      # second level lists correspond to the five basic chord types in the order Maj, min, Dim, dom, mb5
      # bottom level is 'old school', 'new school'
      self.majorKeyScaleGrid =[\
      [['ionian', 'lydian'],       ['dorian', 'minor_major'], ['mixolydian', 'lydian_dominant'], ['diminished2', 'diminished'], ['locrian9', 'locrian']],\
      [['ionian', 'melodic6'],    ['dorian', 'melodic_major3'],['mixolydian', 'altered'],        ['diminished2', 'diminished2'],['locrian', 'locrian']],\
      [['ionian', 'lydian'],       ['dorian', 'dorian'],       ['mixolydian', 'mixolydian'],     ['diminished', 'diminished'],  ['locrian9', 'locrian9']],\
      [['lydian', 'lydian'],       ['dorian', 'melodic4'],     ['mixolydian', 'altered'],        ['diminished2', 'diminished2'],['locrian', 'locrian']],\
      [['ionian', 'melodic_major'],['phrygian', 'phrygian'],   ['melodic5', 'melodic5'],         ['diminished2', 'diminished2'],['locrian', 'locrian']],\
      [['lydian', 'lydian'],       ['dorian', 'melodic4'],    ['mixolydian', 'lydian_dominant'], ['diminished', 'diminished2'], ['locrian9', 'locrian9']],\
      [['lydian', 'lydian'],       ['phrygian', 'melodic4'],   ['mixolydian', 'altered'],        ['diminished', 'diminished'],  ['locrian', 'locrian']],\
      [['ionian', 'lydian'],       ['dorian', 'melodic4'],    ['mixolydian', 'lydian_dominant'], ['diminished2', 'diminished2'],['locrian9', 'locrian9']],\
      [['lydian', 'melodic6'],    ['dorian', 'melodic_major3'],['mixolydian', 'altered'],        ['diminished', 'diminished'],  ['locrian', 'locrian']],\
      [['ionian', 'melodic_major'],['aeolian', 'aeolian'],    ['aeolian_major', 'aeolian_major'],['diminished', 'diminished'],  ['locrian9', 'locrian9']],\
      [['lydian', 'lydian'],       ['dorian', 'melodic4'],     ['mixolydian', 'altered'],        ['diminished2', 'diminished2'],['locrian9', 'locrian9']],\
      [['ionian', 'melodic_major'],['phrygian', 'phrygian'],   ['melodic5', 'melodic5'],         ['diminished', 'diminished'],  ['locrian', 'locrian']]]
      self.minorKeyScaleGrid =[\
      [['ionian', ''],['aeolian', 'minor_melodic'],['', ''],['diminished', 'diminished'],['', '']],\
      [['', ''],['', ''],['', ''],['diminished2', 'diminished2'],['', '']],\
      [['', ''],['phrygian', ''],['', ''],['diminished', 'diminished2'],['locrian', 'melodic2']],\
      [['ionian', 'melodic3'],['', ''],['', ''],['diminished', 'diminished'],['', '']],\
      [['', ''],['', ''],['', ''],['diminished2', 'melodic7'],['', '']],\
      [['', ''],['dorian', 'melodic4'],['', ''],['diminished', 'diminished2'],['', '']],\
      [['', ''],['', ''],['', ''],['diminished', 'melodic7'],['', '']],\
      [['', ''],['aeolian', ''],['mixolydian', 'melodic5'],['diminished2', 'diminished2'],['', '']],\
      [['lydian', 'melodic6'],['', ''],['', ''],['diminished', 'diminished2'],['', '']],\
      [['', ''],['phrygian', ''],['', ''],['diminished', 'diminished'],['locrian', '']],\
      [['ionian', ''],['', ''],['mixolydian', ''],['diminished2', 'diminished2'],['', '']],\
      [['', ''],['', ''],['', ''],['diminished', 'melodic7'],['', '']]]
      # initialise the GUI
      self.d = Display("Harmonic Structure", 800, 240, 10, 10, Color.WHITE)
      self.label01 = Label("key:                "); self.label01.setFont(Font("Verdana",Font.BOLD,20))
      self.label02 = Label("no key"); self.label02.setFont(Font("Verdana",Font.PLAIN,16))
      self.label03 = Label("manual entry"); self.label03.setFont(Font("Verdana",Font.PLAIN,16))
      self.label04 = Label("read from file"); self.label04.setFont(Font("Verdana",Font.PLAIN,16))
      self.label05 = Label("analysed from file"); self.label05.setFont(Font("Verdana",Font.PLAIN,16))
      self.label06 = Label("with ii-V mods"); self.label06.setFont(Font("Verdana",Font.PLAIN,16))
      self.label07 = Label("with ii-V-I mods"); self.label07.setFont(Font("Verdana",Font.PLAIN,16))
      self.label08 = Label("with all mods"); self.label08.setFont(Font("Verdana",Font.PLAIN,16))
      self.label13 = Label("           "); self.label13.setFont(Font("Verdana",Font.PLAIN,16)); self.label13.setForegroundColor(Color.BLUE)
      self.label14 = Label("           "); self.label14.setFont(Font("Verdana",Font.PLAIN,16)); self.label14.setForegroundColor(Color.BLUE)
      self.label15 = Label("           "); self.label15.setFont(Font("Verdana",Font.PLAIN,16)); self.label15.setForegroundColor(Color.BLUE)
      self.label16 = Label("           "); self.label16.setFont(Font("Verdana",Font.PLAIN,16)); self.label16.setForegroundColor(Color.BLUE)
      self.label17 = Label("           "); self.label17.setFont(Font("Verdana",Font.PLAIN,16)); self.label17.setForegroundColor(Color.BLUE)
      self.label18 = Label("           "); self.label18.setFont(Font("Verdana",Font.PLAIN,16)); self.label18.setForegroundColor(Color.BLUE)
      self.label41 = Label("chord:                       "); self.label41.setFont(Font("Verdana",Font.BOLD,20))
      self.label71 = Label("beat:       bar:      "); self.label71.setFont(Font("Verdana",Font.BOLD,20))
      self.tf01 = TextField("", 5, self.ManualKeyEntered)
      self.toggle02 = Toggle(0,0,20,20,True,self.Toggle02,Color.YELLOW,Color.LIGHT_GRAY,Color.BLUE,2)
      self.toggle03 = Toggle(0,0,20,20,False,self.Toggle03,Color.YELLOW,Color.LIGHT_GRAY,Color.BLUE,2)
      self.toggle04 = Toggle(0,0,20,20,False,self.Toggle04,Color.YELLOW,Color.LIGHT_GRAY,Color.BLUE,2)
      self.toggle05 = Toggle(0,0,20,20,False,self.Toggle05,Color.YELLOW,Color.LIGHT_GRAY,Color.BLUE,2)
      self.toggle06 = Toggle(0,0,20,20,False,self.Toggle06,Color.YELLOW,Color.LIGHT_GRAY,Color.BLUE,2)
      self.toggle07 = Toggle(0,0,20,20,False,self.Toggle07,Color.YELLOW,Color.LIGHT_GRAY,Color.BLUE,2)
      self.toggle08 = Toggle(0,0,20,20,False,self.Toggle08,Color.YELLOW,Color.LIGHT_GRAY,Color.BLUE,2)
      if textFile is not None:
         self.InitiateWithTextFile(textFile)
         self.BeatsToNextI()
         self.StartGUI()
      else:
         print "No text file specified for HarmonicStructure.\n"
      for b in range(len(self.chordBases)):
         for s in range(len(self.chordBases[b])):
            break
            print self.selectScale(self.keyBases1[b][s], self.keyTypes1[b][s], self.chordBases[b][s], self.chordTypes[b][s], self.chordExtns[b][s], 'old')

   # ------------------------------------------------------------------------------------
   #                         Functions for Information Passing
   # ------------------------------------------------------------------------------------
   def setUrlinieReference(self, reference):
      self.UL = reference

   def setPlayerReference(self, reference):
      self.PP = reference

   def sendScale(self):
      if self.PP is not None:
         b = self.thisBar
         n = self.thisBeat
         self.PP.setScale(self.getScale(self.selectScale(self.keyBases1[b][n], self.keyTypes1[b][n], self.chordBases[b][n], self.chordTypes[b][n])), self.chordBases[b][n])

   def PrintKeys(self):
      # test function: print out the 'keyBases3' list in the terminal window
      print self.keyBases3
      print self.keyBases4

   def PrintChords(self):
      # print out the 'chordBases' list in the terminal window
      print self.chordBases
      print self.chordTypes

   def BeatsToNextI(self):
      # work out how many beats there are until the next I - returns 0 if currently at a I
      # set up local variables
      b = self.thisBar # 'b' for 'bar'
      n = self.thisBeat # 'n' for 'note'
      b_answer = 0
      n_answer = 0
      found = False
      current_I = self.I_singleKey[b][n]
      if current_I is False: # we're not currently at I
         while b < len(self.I_singleKey): # go through the bars, starting at the current bar
            while n < len(self.I_singleKey[b]): # go through the beats, starting at the current beat
               if self.I_singleKey[b][n] is True: # the indexed bar & beat has been identified as a I
                  b_answer = b-self.thisBar-1 # how many more bars on from this one
                  n_answer = n # beat position in the bar
                  found = True
               if found is True:
                  break
               n += 1
            if found is True:
               break
            n = 0
            b += 1
      return n_answer+(len(self.chordBases[0])*b_answer)

   def BeatsPerBar(self):
      return len(self.chordBases[0])

   def RootOfNextI(self):
      b = self.thisBar # 'b' for 'bar'
      n = self.thisBeat # 'n' for 'note'
      answer = -1
      found = False
      current_I = self.I_singleKey[b][n]
      if current_I is False: # we're not currently at I
         while b < len(self.I_singleKey): # go through the bars, starting at the current bar
            while n < len(self.I_singleKey[b]): # go through the beats, starting at the current beat
               if self.I_singleKey[b][n] is True: # the indexed bar & beat has been identified as a I
                  answer = self.keyBases1[b][n]
                  found = True
               if found is True:
                  break
               n += 1
            if found is True:
               break
            n = 0
            b += 1
      return answer

   def RootAndTypeOfNextI(self):
      b = self.thisBar # 'b' for 'bar'
      n = self.thisBeat # 'n' for 'note'
      root = -1
      kind = ""
      found = False
      current_I = self.I_singleKey[b][n]
      if current_I is False: # we're not currently at I
         while b < len(self.I_singleKey): # go through the bars, starting at the current bar
            while n < len(self.I_singleKey[b]): # go through the beats, starting at the current beat
               if self.I_singleKey[b][n] is True: # the indexed bar & beat has been identified as a I
                  root = self.keyBases1[b][n]
                  kind = self.keyTypes1[b][n]
                  found = True
               if found is True:
                  break
               n += 1
            if found is True:
               break
            n = 0
            b += 1
      return root, kind


   # ------------------------------------------------------------------------------------
   #                                       GUI
   # ------------------------------------------------------------------------------------
   def StartGUI(self):
      self.d.add(self.label01, 25, 6)
      self.d.add(self.label02, 50, 40)
      self.d.add(self.label03, 50, 60)
      self.d.add(self.label04, 50, 80)
      self.d.add(self.label05, 50, 100)
      self.d.add(self.label06, 50, 120)
      self.d.add(self.label07, 50, 140)
      self.d.add(self.label08, 50, 160)
      self.d.add(self.label13, 230, 60)
      self.d.add(self.label14, 230, 80)
      self.d.add(self.label15, 230, 100)
      self.d.add(self.label16, 230, 120)
      self.d.add(self.label17, 230, 140)
      self.d.add(self.label18, 230, 160)
      self.d.add(self.label41, 230, 6)
      self.d.add(self.label71, 570, 6)
      self.d.add(self.tf01, 170, 60)
      self.d.add(self.toggle02, 20, 40)
      self.d.add(self.toggle03, 20, 60)
      self.d.add(self.toggle04, 20, 80)
      self.d.add(self.toggle05, 20, 100)
      self.d.add(self.toggle06, 20, 120)
      self.d.add(self.toggle07, 20, 140)
      self.d.add(self.toggle08, 20, 160)
      self.label13.setText(self.MIDItoNoteName(self.keyBaseManual)+" "+self.keyTypeManual)
      self.label14.setText(self.MIDItoNoteName(self.keyBases0[self.thisBar][self.thisBeat])+" "+self.keyTypes0[self.thisBar][self.thisBeat])
      self.label15.setText(self.MIDItoNoteName(self.keyBases1[self.thisBar][self.thisBeat])+" "+self.keyTypes1[self.thisBar][self.thisBeat])
      self.label16.setText(self.MIDItoNoteName(self.keyBases2[self.thisBar][self.thisBeat])+" "+self.keyTypes1[self.thisBar][self.thisBeat])
      self.label17.setText(self.MIDItoNoteName(self.keyBases3[self.thisBar][self.thisBeat])+" "+self.keyTypes2[self.thisBar][self.thisBeat])
      self.label18.setText(self.MIDItoNoteName(self.keyBases4[self.thisBar][self.thisBeat])+" "+self.keyTypes2[self.thisBar][self.thisBeat])
      self.label41.setText("chord: "+self.MIDItoNoteName(self.chordBases[0][0])+" "+self.chordTypes[0][0]+" "+self.chordExtns[0][0])
   def ManualKeyEntered(self, key): # the user has entered something in the manual key box and pressed enter
      root, kind, c = self.BreakDownChordSymbol(key)
      if kind in ['Maj', 'min']:
         self.keyBaseManual = self.NoteNameToMIDI(root)
         self.keyTypeManual = kind
         self.label13.setText(self.MIDItoNoteName(self.keyBaseManual)+" "+self.keyTypeManual)
   def Toggle02(self, newState): # 'no key' has been toggled
      if newState == True:
         self.toggle08.setValue(False)
         self.toggle07.setValue(False)
         self.toggle06.setValue(False)
         self.toggle05.setValue(False)
         self.toggle04.setValue(False)
         self.toggle03.setValue(False)
         self.keyMode = 0
      else:
         if self.toggle03.getValue() is False and self.toggle04.getValue() is False and\
         self.toggle05.getValue() is False and self.toggle06.getValue() is False and\
         self.toggle07.getValue() is False and self.toggle08.getValue() is False:
            self.toggle02.setValue(True)
   def Toggle03(self, newState): # 'manual' has been toggled
      if newState == True:
         self.toggle08.setValue(False)
         self.toggle07.setValue(False)
         self.toggle06.setValue(False)
         self.toggle05.setValue(False)
         self.toggle04.setValue(False)
         self.toggle02.setValue(False)
         self.keyMode = 1
      else:
         if self.toggle02.getValue() is False and self.toggle04.getValue() is False and\
         self.toggle05.getValue() is False and self.toggle06.getValue() is False and\
         self.toggle07.getValue() is False and self.toggle08.getValue() is False:
            self.toggle02.setValue(True)
   def Toggle04(self, newState): # 'from file' has been toggled
      if newState == True:
         self.toggle08.setValue(False)
         self.toggle07.setValue(False)
         self.toggle06.setValue(False)
         self.toggle05.setValue(False)
         self.toggle03.setValue(False)
         self.toggle02.setValue(False)
         self.keyMode = 2
      else:
         if self.toggle02.getValue() is False and self.toggle03.getValue() is False and\
         self.toggle05.getValue() is False and self.toggle06.getValue() is False and\
         self.toggle07.getValue() is False and self.toggle08.getValue() is False:
            self.toggle02.setValue(True)
   def Toggle05(self, newState): # 'analysis - single key' has been toggled
      if newState == True:
         self.toggle02.setValue(False)
         self.toggle03.setValue(False)
         self.toggle04.setValue(False)
         self.toggle06.setValue(False)
         self.toggle07.setValue(False)
         self.toggle08.setValue(False)
         self.keyMode = 3
      else:
         if self.toggle02.getValue() is False and self.toggle03.getValue() is False and\
         self.toggle04.getValue() is False and self.toggle06.getValue() is False and\
         self.toggle07.getValue() is False and self.toggle08.getValue() is False:
            self.toggle02.setValue(True)
   def Toggle06(self, newState): # 'analysis - with ii-V modulations' has been toggled
      if newState == True:
         self.toggle02.setValue(False)
         self.toggle03.setValue(False)
         self.toggle04.setValue(False)
         self.toggle05.setValue(False)
         self.toggle07.setValue(False)
         self.toggle08.setValue(False)
         self.keyMode = 4
      else:
         if self.toggle02.getValue() is False and self.toggle03.getValue() is False and\
         self.toggle04.getValue() is False and self.toggle05.getValue() is False and\
         self.toggle07.getValue() is False and self.toggle08.getValue() is False:
            self.toggle02.setValue(True)
   def Toggle07(self, newState): # 'analysis - with ii-V-I modulations' has been toggled
      if newState == True:
         self.toggle02.setValue(False)
         self.toggle03.setValue(False)
         self.toggle04.setValue(False)
         self.toggle05.setValue(False)
         self.toggle06.setValue(False)
         self.toggle08.setValue(False)
         self.keyMode = 5
      else:
         if self.toggle02.getValue() is False and self.toggle03.getValue() is False and\
         self.toggle04.getValue() is False and self.toggle05.getValue() is False and\
         self.toggle06.getValue() is False and self.toggle08.getValue() is False:
            self.toggle02.setValue(True)
   def Toggle08(self, newState): # 'analysis - with ii-V and ii-V-I modulations' has been toggled
      if newState == True:
         self.toggle02.setValue(False)
         self.toggle03.setValue(False)
         self.toggle04.setValue(False)
         self.toggle05.setValue(False)
         self.toggle06.setValue(False)
         self.toggle07.setValue(False)
         self.keyMode = 6
      else:
         if self.toggle02.getValue() is False and self.toggle03.getValue() is False and\
         self.toggle04.getValue() is False and self.toggle05.getValue() is False and\
         self.toggle06.getValue() is False and self.toggle07.getValue() is False:
            self.toggle02.setValue(True)

   # ------------------------------------------------------------------------------------
   #                              Main Control Functions
   # ------------------------------------------------------------------------------------
   def InitiateWithTextFile(self, textFile):
      # set up some temporary variables and read in the text file
      result, key_from_file = self.ReadChords(textFile)
      keyBase_from_file = -1
      keyType_from_file = ""
      foundKeyInFile = False
      if key_from_file != "": # a key was read in from the text file
         keyBase_from_file, keyType_from_file, c = self.BreakDownChordSymbol(key_from_file)
         keyBase_from_file = self.NoteNameToMIDI(keyBase_from_file)
         foundKeyInFile = True
      if result:
         for bar in result:
            Ba = [] # set up empty lists for the new bars - list for chord bases
            Bb = [] # list for chord types
            Bc = [] # list for chord extensions
            Bd = [] # list for key bases (if applicable)
            Be = [] # list for key types (if applicable)
            for symbol in bar:
               a, b, c = self.BreakDownChordSymbol(symbol) # a is the chord letter, b is the chord type, c is anything left over
               Ba.append(self.NoteNameToMIDI(a)) # converts the chord letter to a MIDI number (C=0...)
               Bb.append(b)
               Bc.append(c)
               if foundKeyInFile:
                  Bd.append(keyBase_from_file)
                  Be.append(keyType_from_file)
               else:
                  Bd.append(-1)
                  Be.append("")
            self.chordBases.append(Ba) # put the one-bar list into the overall list
            self.chordTypes.append(Bb)
            self.chordExtns.append(Bc)
            self.keyBases0.append(Bd)
            self.keyTypes0.append(Be)

      # we now have lists of the chord bases, types and extensions from the text file
      # we need to extract the chord sequence (i.e. every change, rather than a chord per beat)
      chord_base_sequence, chord_type_sequence, chord_change_index = self.GetChordSequence()
      # now analyse the sequence for key-related features
      key, key_type, key2, key3, key4, key_type2 = self.BruteForceAnalysis(chord_base_sequence, chord_type_sequence, chord_change_index)
      print "key from file: "+str(keyBase_from_file)+keyType_from_file
      print "key from analysis: "+str(key[0])+key_type[0]
      # re-align these with the beats/bars lists (noting it's currently based on the changes only)
      # but only if key wasn't identified in the file
      self.keyBases1, self.keyTypes1 = self.RealignChords(key, key_type, chord_change_index)
      self.keyBases2, self.keyTypes1 = self.RealignChords(key2, key_type, chord_change_index)
      self.keyBases3, self.keyTypes2 = self.RealignChords(key3, key_type2, chord_change_index)
      self.keyBases4, self.keyTypes2 = self.RealignChords(key4, key_type2, chord_change_index)
      # Now do searches for I chords
      self.I_singleKey = self.TwoTrue(self.AnalyseSameness(self.chordBases, self.keyBases1), self.AnalyseSameness(self.chordTypes, self.keyTypes1))

      # the Tap function defines the actions to be taken upon receiving a 'tap' signal,
      # expected to come from a timekeeper. The actions involve advancing the placekeeper

   def Tick(self):
      self.tickTimer.start()

   def TickInternal(self):
      if self.thisTick < self.ticksPerBar-1:
         self.thisTick += 1
      else:
         self.thisTick = 0
      if self.thisTick%12 == 0: # it's a crotchet beat
         self.Tap()

   def getTickCount(self):
      return self.thisTick

   def Tap(self):
      # advance the beat counter
      if self.thisBeat >= len(self.chordBases[0])-1: # we are at (or beyond) the end of the bar
         self.thisBeat = 0
         if self.thisBar >= len(self.chordBases)-1: # we are at (or beyond) the end of the chord chart
            self.thisBar = 0 # go back to the start of the chord chart
         else:
            self.thisBar += 1 # not at the end of the chord chart; advance the bar counter by 1
      else:
         self.thisBeat += 1 # not at the end of the bar; advance the beat counter by 1
      beat = self.thisBeat
      bar = self.thisBar
      # first update the relevant variables
      if self.keyMode == 0: # no key
         self.thisKeyBase = -1; self.thisKeyType = ""
      elif self.keyMode == 1: # key as entered in the GUI
         self.thisKeyBase = self.keyBaseManual; self.thisKeyType = self.keyTypeManual
      elif self.keyMode == 2: # key as read in from text file
         self.thisKeyBase = self.keyBases0[bar][beat]; self.thisKeyType = self.keyTypes0[bar][beat]
      elif self.keyMode == 3: # key as read in from text file
         self.thisKeyBase = self.keyBases1[bar][beat]; self.thisKeyType = self.keyTypes1[bar][beat]
      elif self.keyMode == 4: # key as read in from text file
         self.thisKeyBase = self.keyBases2[bar][beat]; self.thisKeyType = self.keyTypes1[bar][beat]
      elif self.keyMode == 5: # key as read in from text file
         self.thisKeyBase = self.keyBases3[bar][beat]; self.thisKeyType = self.keyTypes2[bar][beat]
      elif self.keyMode == 6: # key as read in from text file
         self.thisKeyBase = self.keyBases4[bar][beat]; self.thisKeyType = self.keyTypes2[bar][beat]
      # then update the relevant GUI fields
      self.label71.setText("beat: "+str(beat+1)+"  bar: "+str(bar+1))
      self.label41.setText("chord: "+self.MIDItoNoteName(self.chordBases[bar][beat])+" "+self.chordTypes[bar][beat]+" "+self.chordExtns[bar][beat])
      self.label01.setText("key: "+self.MIDItoNoteName(self.thisKeyBase)+" "+self.thisKeyType)
      self.label14.setText(self.MIDItoNoteName(self.keyBases0[bar][beat])+" "+self.keyTypes0[bar][beat])
      self.label15.setText(self.MIDItoNoteName(self.keyBases1[bar][beat])+" "+self.keyTypes1[bar][beat])
      self.label16.setText(self.MIDItoNoteName(self.keyBases2[bar][beat])+" "+self.keyTypes1[bar][beat])
      self.label17.setText(self.MIDItoNoteName(self.keyBases3[bar][beat])+" "+self.keyTypes2[bar][beat])
      self.label18.setText(self.MIDItoNoteName(self.keyBases4[bar][beat])+" "+self.keyTypes2[bar][beat])
      # send the latest chord information to the player
      self.sendScale()
      self.PP.beat()
      # if it's the first beat, send a 'new bar' event to the Urlinie (for testing purposes)
      #if self.thisBeat == 0:
      #   self.UL.newBar(self.thisBar)

   def CurrentBeat(self):
      return self.thisBeat

   # ------------------------------------------------------------------------------------
   #                    Functions for Scale Theory and Chord Type
   # ------------------------------------------------------------------------------------
   def selectScale(self, key_base, key_type, chord_base, chord_type, chord_extn=None, school=None):
      if chord_extn is None:
         chord_extn = ""
      # 'school' will be either 'new' or not 'new'
      # set up container for the result
      scale_choice = "" #
      # convert the chord type into an index number
      chord_number = 0
      if chord_type == 'Maj':
         chord_number = 0
      elif chord_type == 'min':
         chord_number = 1
      elif chord_type == 'Dom':
         chord_number = 2
      elif chord_type == 'dim':
         chord_number = 3
      elif chord_type == 'mb5':
         chord_number = 4
      # convert the school type into an index number
      school_number = 0
      if school == 'new':
         school_number = 1
      # ensure chord_base is in the range 0-11
      chord_base = int(chord_base)%12
      # key_base outside of the 0-11 range, or key_type != Maj/min, indicates no particular key or unknown key
      if key_base >= 0 and key_base < 12 and key_type in ['Maj', 'min']: # we do have key information
         key_base = int(key_base) # just making sure - we already know it's in the 0-11 range but it might be a float
         root_position = chord_base - key_base # interval between key and chord in semitones
         if root_position < 0:
            root_position += 12 # make sure it's in the range 0-11
         elif root_position > 11:
            root_position -= 12
         if key_type == 'Maj': # pick the scale out of the major key/scale grid
            scale_choice = self.majorKeyScaleGrid[root_position][chord_number][school_number]
         elif key_type == 'min':
            scale_choice = self.minorKeyScaleGrid[root_position][chord_number][school_number]
         return scale_choice
   def getScale(self, scale_name=None):
      # this function gives the degrees of the scale starting with tonic = 0
      # in each case, the 3-7 can be found by taking the 3rd and 7th degree in the list
      # (that is, index 0 and 6); this works naturally with every scale except for
      # the major blues, which has been arranged such as to achieve this
      if scale_name == 'ionian':
         return [0, 2, 4, 5, 7, 9, 11]
      elif scale_name == 'dorian':
         return [0, 2, 3, 5, 7, 9, 10]
      elif scale_name == 'phrygian':
         return [0, 1, 3, 5, 7, 8, 10]
      elif scale_name == 'lydian':
         return [0, 2, 4, 6, 7, 9, 11]
      elif scale_name == 'mixolydian':
         return [0, 2, 4, 5, 7, 9, 10]
      elif scale_name == 'aeolian':
         return [0, 2, 3, 5, 7, 8, 10]
      elif scale_name == 'locrian':
         return [0, 1, 3, 5, 6, 8, 10]
      elif scale_name == 'locrian9':
         return [0, 2, 3, 5, 6, 8, 10]
      elif scale_name == 'minor_harmonic':
         return [0, 2, 3, 5, 7, 8, 11]
      elif scale_name == 'minor_melodic':
         return [0, 2, 3, 5, 7, 9, 11]
      elif scale_name == 'aeolian_major':
         return [0, 2, 4, 5, 7, 8, 10]
      elif scale_name == 'diminished':
         return [0, 2, 3, 5, 6, 8, 9, 11]
      elif scale_name == 'diminished2':
         return [0, 1, 3, 4, 6, 7, 9, 10]
      elif scale_name == 'lydian_dominant':
         return [0, 2, 4, 6, 7, 9, 10]
      elif scale_name == 'minor_major':
         return [0, 2, 3, 5, 7, 9, 11]
      elif scale_name == 'melodic_major':
         return [0, 1, 4, 5, 7, 8, 11]
      elif scale_name == 'melodic_major3':
         return [0, 1, 3, 4, 7, 8, 10]
      elif scale_name == 'blues':
         return [0, 2, 3, 5, 6, 7, 10]
      elif scale_name == 'blues_major':
         return [0, 3, 4, 7, 9, 12, 14]
      elif scale_name == 'melodic7':
         return [0, 1, 3, 4, 6, 8, 9]
      elif scale_name == 'melodic6':
         return [0, 3, 4, 6, 7, 9, 11]
      elif scale_name == 'melodic5':
         return [0, 1, 4, 5, 7, 8, 10]
      elif scale_name == 'melodic4':
         return [0, 2, 3, 6, 7, 9, 10]
      elif scale_name == 'melodic3':
         return [0, 2, 4, 5, 8, 9, 11]
      elif scale_name == 'melodic2':
         return [0, 1, 3, 5, 6, 9, 10]
      elif scale_name == 'altered':
         return [0, 1, 3, 4, 6, 8, 10]
      else:
         return []

   # ------------------------------------------------------------------------------------
   #                            Functions for Key Analysis
   # ------------------------------------------------------------------------------------
      # the FlattenListOfLists function takes the "bars with beats" structure and flattens
      # it to just have the beats with no bars
   def FlattenListOfLists(self, listOfLists):
      return [item for sublist in listOfLists for item in sublist]


      # the GetChordSequence function accesses the Class variables that hold the lists of
      # chords (at every beat of every bar) and breaks it down to just the chord sequence
      # without any beat-by-beat repeats
   def GetChordSequence(self):
      bases_flat = self.FlattenListOfLists(self.chordBases)
      types_flat = self.FlattenListOfLists(self.chordTypes)
      chord_base_sequence = []
      chord_type_sequence = []
      chord_change_index = []
      this_base = -1
      this_type = ""
      for i in range(len(bases_flat)):
         if bases_flat[i] != this_base or types_flat[i] != this_type:
            chord_base_sequence.append(bases_flat[i])
            chord_type_sequence.append(types_flat[i])
            chord_change_index.append(i)
            this_base = bases_flat[i]
            this_type = types_flat[i]
      return chord_base_sequence, chord_type_sequence, chord_change_index

      # the RealignChords function takes a list that currently aligns with the chord changes,
      # and constructs a beat-by-beat list of lists (i.e. beats in bars), using the change
      # indexes to determine the placement of the changes.
   def RealignChords(self, key_list, type_list, change_indexes):
      change_indexes.append(len(self.FlattenListOfLists(self.chordBases))+1)
      aligned_bases = []
      aligned_types = []
      counter = 0
      index = 0
      for bar in self.chordBases:
         these_bases = []
         these_types = []
         for beat in bar:
            if counter < change_indexes[index+1]:
               these_bases.append(key_list[index])
               these_types.append(type_list[index])
            else:
               index += 1
               these_bases.append(key_list[index])
               these_types.append(type_list[index])
            counter += 1
         aligned_bases.append(these_bases)
         aligned_types.append(these_types)
      return aligned_bases, aligned_types

      # the BruteForceAnalysis function tries every major and minor key to see which one
      # appears to be the best match for the given chord sequence; it initially selects a single
      # key for the whole chord sequence. It then searches for instances of ii-V and ii-V-I sequences -
      # limited to cases where the V is dominant - and it treats them as modulations
      # it returns several versions of the key map:
      # 1. single key for whole chord chart
      # 2. key base changes for ii-V sequences
      # 3. key base and type changes for ii-V-I sequences
      # 4. version 3 plus version 2 (where the ii-V's are not ii-V-I's)
   def BruteForceAnalysis(self, chord_base_sequence, chord_type_sequence, chord_change_index):
      # Try all major keys using common major modal theory
      all_key_roles = []
      for keyNo in range(12):
         this_key_roles = []
         for i in range(len(chord_base_sequence)):
            chromatic_degree = chord_base_sequence[i]-keyNo
            if chromatic_degree < 0:
               chromatic_degree += 12
            if chromatic_degree > 11:
               chromatic_degree -= 12
            if chord_type_sequence[i] == 'Maj':
               if chromatic_degree == 0:
                  this_key_roles.append(1)
               elif chromatic_degree == 5:
                  this_key_roles.append(4)
               else:
                  this_key_roles.append(0)
            elif chord_type_sequence[i] == 'min':
               if chromatic_degree == 2:
                  this_key_roles.append(2)
               elif chromatic_degree == 4:
                  this_key_roles.append(3)
               elif chromatic_degree == 9:
                  this_key_roles.append(6)
               else:
                  this_key_roles.append(0)
            elif chord_type_sequence[i] == 'Dom':
               if chromatic_degree == 7:
                  this_key_roles.append(5)
               else:
                  this_key_roles.append(0)
            elif chord_type_sequence[i] == 'mb5':
               if chromatic_degree == 11:
                  this_key_roles.append(7)
               else:
                  this_key_roles.append(0)
            else:
               this_key_roles.append(0)
         all_key_roles.append(this_key_roles)
      # Try all harmonic minor modes
      for keyNo in range(12):
         this_key_roles = []
         for i in range(len(chord_base_sequence)):
            chromatic_degree = chord_base_sequence[i]-keyNo
            if chromatic_degree < 0:
               chromatic_degree += 12
            if chromatic_degree > 11:
               chromatic_degree -= 12
            if chord_type_sequence[i] == 'min':
               if chromatic_degree == 0:
                  this_key_roles.append(1)
               elif chromatic_degree == 5:
                  this_key_roles.append(4)
               else:
                  this_key_roles.append(0)
            elif chord_type_sequence[i] == 'Maj':
               if chromatic_degree == 3:
                  this_key_roles.append(3)
               elif chromatic_degree == 8:
                  this_key_roles.append(6)
               else:
                  this_key_roles.append(0)
            elif chord_type_sequence[i] == 'Dom':
               if chromatic_degree == 7:
                  this_key_roles.append(5)
               else:
                  this_key_roles.append(0)
            elif chord_type_sequence[i] == 'mb5':
               if chromatic_degree == 2:
                  this_key_roles.append(2)
               else:
                  this_key_roles.append(0)
            elif chord_type_sequence[i] == 'dim':
               if chromatic_degree == 11:
                  this_key_roles.append(7)
               else:
                  this_key_roles.append(0)
            else:
               this_key_roles.append(0)
         all_key_roles.append(this_key_roles)
      # now tally the resulting hits
      count = []
      Is = []
      Vs = []
      V_indexes = []
      for k in range(len(all_key_roles)):
         chord_count = 0
         I_count = 0
         V_count = 0
         V_indexes_this_key = []
         for e in range(len(all_key_roles[k])):
            if all_key_roles[k][e] != 0:
               chord_count += 1
               if all_key_roles[k][e] == 1:
                  I_count += 1
               elif all_key_roles[k][e] == 5:
                  V_count += 1
                  V_indexes_this_key.append(e)
         count.append(chord_count)
         Is.append(I_count)
         Vs.append(V_count)
         V_indexes.append(V_indexes_this_key)
      # we have the number of chords consistent with each key, as well as the number of I's and V's
      # we also have the indexes of all V chords
      # check which V's are part of a ii-V (ii can be any chord type)
      iiV_indexes = []
      iiVI_indexes = []
      iiVI_types = []
      for k in range(len(V_indexes)):
         iiV_indexes_this_key = []
         iiVI_indexes_this_key = []
         iiVI_types_this_key = []
         for i in range(len(V_indexes[k])):
            if V_indexes[k][i] > 0: # there's a V chord index with at least one chord before it
               if chord_base_sequence[V_indexes[k][i]] - chord_base_sequence[V_indexes[k][i]-1] in [5, -7]: # the previous chord has degree 2
                  iiV_indexes_this_key.append(V_indexes[k][i]) # save the index of the V
                  if V_indexes[k][i] < len(chord_base_sequence)-1: # there's at least one chord after the V chord
                     if chord_base_sequence[V_indexes[k][i]] - chord_base_sequence[V_indexes[k][i]+1] in [-5, 7]: # the next chord has degree 0
                        iiVI_indexes_this_key.append(V_indexes[k][i]) # save the index of the V
                        iiVI_types_this_key.append(chord_type_sequence[V_indexes[k][i]+1])
         iiV_indexes.append(iiV_indexes_this_key) # all of the V's that are part of a ii-V
         iiVI_indexes.append(iiVI_indexes_this_key) # all of the V's that are part of a ii-V-I
         iiVI_types.append(iiVI_types_this_key) # the key of the I where the V is part of a ii-V-I
         # note that the key choice needs to be constrained to Maj or min, while the type here could be any of the 5 chord types
         # this needs to be taken into account

      # Now create a scoring function of "consistent chords" * ("I's"+"V's")
      key_scores = [a*(b+c) for a, b, c in zip(count, Is, Vs)]
      max_key_score = max(key_scores)
      key_result = -1
      key_result_type = ""
      for i in range(len(key_scores)):
         if key_scores[i] == max_key_score:
            key_result = i
      if key_result < 12:
         key_result_type = 'Maj'
      else:
         key_result -= 12
         key_result_type = 'min'
      # now make lists out of the key and key type (homogeneous, i.e. same key)
      key_base_sequence = []
      key_type_sequence = []
      for chord in chord_base_sequence:
         key_base_sequence.append(key_result)
         key_type_sequence.append(key_result_type)
      # now modify the key base sequence to include the ii-V (etc) modulations
      # first make copies
      key_base_seq_with_ii_Vs = []
      key_base_seq_with_ii_V_Is = []
      key_base_seq_with_ii_Vs_and_ii_V_Is = []
      for key_base in key_base_sequence:
         key_base_seq_with_ii_Vs.append(key_base)
         key_base_seq_with_ii_V_Is.append(key_base)
         key_base_seq_with_ii_Vs_and_ii_V_Is.append(key_base)
      key_type_sequence_with_ii_V_Is = []
      for key_t in key_type_sequence:
         key_type_sequence_with_ii_V_Is.append(key_t)
      # now modify the ii-V's
      for k in range(len(iiV_indexes[0:12])): # go through the ii-V indexes list key by key, just the Majors
         # (since the ii-V analysis produces the same results for Maj or min)
         for index in iiV_indexes[k]:
            key_base_seq_with_ii_Vs[index] = k
            key_base_seq_with_ii_Vs[index-1] = k
            key_base_seq_with_ii_Vs_and_ii_V_Is[index] = k
            key_base_seq_with_ii_Vs_and_ii_V_Is[index-1] = k
      # now do the same for the ii-V-I modulations, but only if the apparent resulting key is Maj or min
      for k in range(len(iiVI_indexes[0:12])):
         for i in range(len(iiVI_indexes[k])):
            if iiVI_types[k][i] in ['Maj', 'min']:
               key_base_seq_with_ii_V_Is[iiVI_indexes[k][i]-1] = k
               key_base_seq_with_ii_V_Is[iiVI_indexes[k][i]] = k
               key_base_seq_with_ii_V_Is[iiVI_indexes[k][i]+1] = k
               key_type_sequence_with_ii_V_Is[iiVI_indexes[k][i]-1] = iiVI_types[k][i]
               key_type_sequence_with_ii_V_Is[iiVI_indexes[k][i]] = iiVI_types[k][i]
               key_type_sequence_with_ii_V_Is[iiVI_indexes[k][i]+1] = iiVI_types[k][i]
               key_base_seq_with_ii_Vs_and_ii_V_Is[iiVI_indexes[k][i]+1] = k
      return key_base_sequence, key_type_sequence, key_base_seq_with_ii_Vs,\
      key_base_seq_with_ii_V_Is, key_base_seq_with_ii_Vs_and_ii_V_Is, key_type_sequence_with_ii_V_Is

      # AnalyseSameness goes through two lists with identical structures and marks a 'True' every
      # beat where they are identical, otherwise 'False'.
   def AnalyseSameness(self, list1, list2): # list1 and list2 MUST have the same length and structure
      result = [] # set up a result list
      for b, bar in enumerate(list1): # go through the bars
         this_bar = []
         for n, note in enumerate(bar): # for each beat
            if list2[b][n] == note: # check if the value of list1 matches the value of list2
               this_bar.append(True) # If yes, mark it True
            else:
               this_bar.append(False) # otherwise, False
         result.append(this_bar)
      return result

   def TwoTrue(self, list1, list2): # basically the same as AnalyseSameness, except it checks for both being 'True'
      result = []
      for b, bar in enumerate(list1):
         this_bar = []
         for n, note in enumerate(bar):
            if note is True and list2[b][n] is True:
               this_bar.append(True)
            else:
               this_bar.append(False)
         result.append(this_bar)
      return result


   # ------------------------------------------------------------------------------------
   #                Functions for Reading In the Chord Chart Text File
   # ------------------------------------------------------------------------------------
      # ReadChords is a function to read the chords in from a text file
      # and store them - one per beat - in bars
   def ReadChords(self, filename=None):
      if filename is None:
         print("Unable to open file, as no file name has been specified\n")
         return 0
      else:
         with open(str(filename)) as f:
            chords_rough = f.readlines()
            # now chords_rough is a list where each list element
            # is a line (as a string) from the file
         fileElements = [] # create an empty list for the file elements
         i_beats = 0 # integer to hold the number of beats per bar (if specified)
         i_beatType = 0 # integer to hold the beat type (if specified)
         key = "" # string to hold key info from file
         for line in chords_rough:
            if line[0] == '%' or line[0] == '#': # first character is '%' or '#'
               pass # it's a comment line; skip it
            elif line == []:
               pass # it's an empty line; skip it
            elif line[0:3] == "key": # the text file contains a key statement
               for i in range(len(line)):
                  if i>2 and lower(line[i]) in "abcdefg": # find the first possible key name letter that's not in the word 'key'
                     key = line[i:].strip() # remove any spaces and newlines from the end
                     break # don't continue checking; the first instance found is assumed to be the correct instance
            elif line[0:7] == "timesig": # this line specifies the time signature in the form a/b
               s_beats = "" # the value read from the file will initially be a string
               s_beatType = ""
               foundEquals = False
               foundBeats = False
               for letter in line:
                  if foundEquals is True:
                     if foundBeats is False:
                        if letter in "0123456789":
                           s_beats = s_beats+letter
                        elif letter == "/":
                           if s_beats != "":
                              foundBeats = True
                     elif letter in "0123456789":
                        s_beatType = s_beatType+letter
                  elif letter == "=":
                     foundEquals = True
               if s_beats != "":
                  i_beats = int(s_beats)
               if s_beatType != "":
                  i_beatType = int(s_beatType)
               if s_beats == "" and s_beatType == "":
                  print "-- no time signature found in text file"
               elif s_beats == "":
                  print "-- time signature specified in text file has unreadable form"
               elif s_beatType == "":
                  print "-- time signature specified in text file has unreadable form"
               print "time signature from text file: "+str(i_beats)+"/"+str(i_beatType)+"."
            else: # every other line that's not comment, blank or timesig
               line = line.split() # break down using whitespace as delimiter
               for element in line: # now take each element in the 'line' list
                  fileElements.append(element) # and append it to the 'file elements' list
         # Now we have a list of all the non-comment, non-timesig elements from the chord chart file.
         # We're going to put them into bars, one chord per beat
         if i_beats == 0: # this would be the case if the text file had no timesig
            i_beats = self.defaultBeatsPerBar # set the default
         bars = []
         this_bar = []
         for element in fileElements: # each element is a single chord or a barline
            if element == '|': # end of a bar
               # insert function to spread the chords out one beat per bar
               # first count the number of chords in the bar;
               no_of_chords = len(this_bar)
               this_bar_every_beat = []
               # if equal or greater than the number of beats, just take them in order (excess chords will be dropped this way)
               if no_of_chords >= i_beats:
                  for number in range(i_beats):
                     this_bar_every_beat.append(this_bar[number])
               # otherwise, determine a distribution
               else:
                  spacing = float(no_of_chords)/float(i_beats) # this tells us the number of chords per beat as a float
                  for number in range(i_beats): # set up a vector [0, 1, ... ,i_beats-1]
                     this_bar_every_beat.append(this_bar[int(spacing*number)])
               bars.append(this_bar_every_beat) # add existing bar to the list of bars
               this_bar = [] # start a fresh new bar
            else:
               this_bar.append(element) # add the chord to the current bar
         return bars, key

      # NoteNameToMIDI is a function for converting the note names to MIDI numbers.
      # It only recognises the names A-G and the symbols # (sharp) and b (flat).
      # It only recognises basic notes, e.g. Bb or F#; no double-flats or double-sharps.
      # Capitals / lower case do not matter, as it converts all incoming strings to 'lower'.
      # The returned MIDI number is in octave zero (C=0, C#=1, D=2, ..., B=11)
   def NoteNameToMIDI(self, noteName):
      n = lower(noteName)
      if n == 'c' or n == 'b#':
         return 0
      elif n == 'c#' or n == 'db':
         return 1
      elif n == 'd':
         return 2
      elif n == 'd#' or n == 'eb':
         return 3
      elif n == 'e' or n == 'fb':
         return 4
      elif n == 'e#' or n == 'f':
         return 5
      elif n == 'f#' or n == 'gb':
         return 6
      elif n == 'g':
         return 7
      elif n == 'g#' or n == 'ab':
         return 8
      elif n == 'a':
         return 9
      elif n == 'a#' or n == 'bb':
         return 10
      elif n == 'b' or n == 'cb':
         return 11
      else:
         print "in HarmonicStructure, NoteNametoMIDI, the note name "+str(n)+" was not recognised;\nreturning it as a 'C'"
         return 0
   def MIDItoNoteName(self, MIDIno):
      if MIDIno == 0:
         return 'C'
      elif MIDIno == 1:
         return 'C#'
      elif MIDIno == 2:
         return 'D'
      elif MIDIno == 3:
         return 'Eb'
      elif MIDIno == 4:
         return 'E'
      elif MIDIno == 5:
         return 'F'
      elif MIDIno == 6:
         return 'F#'
      elif MIDIno == 7:
         return 'G'
      elif MIDIno == 8:
         return 'Ab'
      elif MIDIno == 9:
         return 'A'
      elif MIDIno == 10:
         return 'Bb'
      elif MIDIno == 11:
         return 'B'
      else:
         return '--'

      # The BreakDownChordSymbol function takes a chord symbol which has the format 'note-type-extensions', e.g. C#mb9
      # It extracts out the base note (being a letter A-G optionally followed by # or b), then reads the type as
      # 'Maj' (major) if the letter stands alone, or if 'M' or 'Maj' appears immediately after,
      # 'min' (minor) if 'm', '-' or 'min' appears immediately after.
      # 'Dom' (dominant 7th) if '7', '9', '13' or 'alt' appears immediately after.
      # 'dim' (diminished) if 'd', 'dim' or 'o' appears immediately after.
      # 'mb5' (half-diminished) if it's already been assessed as 'min' and '7b5' appears immediately after.
      # Anything remaining on the chord symbol is retained as an extension, and not analysed.
      # Note also, in the case of a Dom based on '13' or 'alt', the 13 or alt is retained as the extension.
      # So the example C#mb9 has note: C#, type: min, extension: b9.
      # 'Bbalt' would be assessed as note: Bb, type: Dom, extension: alt
      # This function does not attempt to cover every possible case. It could be extended to cover more cases as they come up.
   def BreakDownChordSymbol(self, chordSymbol):
      c = chordSymbol
      # assume the symbol is correctly formatted
      root = c[0]
      c = c[1:] # remove the first character
      kind = "" # this will be Maj, min, Dom, Aug, dim or mb5
      if len(c) > 0: # there's at least a second character
         if c[0] == 'b' or c[0] == '#':
            root += c[0]
            c = c[1:] # remove the 'b' or '#' character
      if len(c) == 0:
         kind = 'Maj'
      elif c[0] == 'M':
         kind = 'Maj'
         c = c[1:]
         if len(c) > 1:
            if lower(c[0:2]) == 'aj':
               c = c[2:]
            elif lower(c[0:2]) == 'in': # someone might write out 'MIN'
               kind = 'min'
               c = c[2:]
            if len(c) > 1:
               if lower(c[0:2]) == 'or': # in case someone writes out 'major' or 'minor'
                  c = c[2:]
      elif c[0] == 'm' or c[0] == '-':
         kind = 'min'
         c = c[1:]
         if len(c) > 1:
            if lower(c[0:2]) == 'in':
               c = c[2:]
            elif lower(c[0:2]) == 'aj': # someone might write out 'maj'
               kind = 'Maj'
               c = c[2:]
            if len(c) > 1:
               if lower(c[0:2]) == 'or':
                  c = c[2:]
      elif c[0] == '7' or c[0] == '9':
         kind = 'Dom'
         c = c[1:]
      elif c[0] == 'o' or c[0] == 'd':
         kind = 'dim'
         c = c[1:]
         if len(c) > 1:
            if lower(c[0:2]) == 'im':
               c = c[2:]
      elif len(c) > 1:
         if c[0:2] == '13':
            kind = 'Dom' # don't strip the '13' since it's an extension
         elif len(c) > 2:
            if lower(c[0:3]) == 'alt':
               kind = 'Dom' # don't strip the word 'alt' since it's an extension
      if kind == 'min' and len(c) > 2:
         if c[0:3] == '7b5':
            kind = 'mb5'
            c = c[3:]
      if len(c) > 0:
         if c[0] == '7' or c[0] == '9':
            c = c[1:]
      # At this point we should have found the root and the basic type
      # and we've stripped off that info. Anything remaining is an extension.
      if kind == "":
         print "Unable to identify chord type '"+str(c)+"'."
      return root, kind, c

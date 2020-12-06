from HarmonicStructure import *
from MIDIInput import *
from Urlinie import *
from NoteSender import *
from MusicXMLWriter import *
from Player import *
#from TimeKeeper import *
from time import sleep

CHORD_CHART = "SatinDoll.txt"
DISPLAY_SCALE = 1.0 #1.0 recommended for regular PC, 2.2 recommended for 'Surface' device

UL = Urlinie(DISPLAY_SCALE)
NS = NoteSender()
XW = MusicXMLWriter()
LS = HarmonicStructure(CHORD_CHART, DISPLAY_SCALE)
MI = MIDIInput(DISPLAY_SCALE)
PP = Player()
#MO = Motif(DISPLAY_SCALE)
#TK = TimeKeeper()
MI.setUrlinieReference(UL)
MI.setLeadSheetReference(LS)
MI.setXMLWriterReference(XW)
MI.setPlayerReference(PP)
MI.setNoteSenderReference(NS)
#MI.setTimeKeeperReference(TK)
#UL.setMIDIInputReference(MI)
#UL.setLeadSheetReference(LS)
#UL.setNoteSenderReference(NS)
LS.setUrlinieReference(UL)
LS.setPlayerReference(PP)
LS.setMIDIInputReference(MI)
NS.setXMLWriterReference(XW)
NS.setPlayerReference(PP)
PP.setUrlinieReference(UL)
PP.setNoteSenderReference(NS)
PP.setLeadSheetReference(LS)
PP.setMIDIInputReference(MI)
#TK.setLeadSheetReference(LS)
PP.getNewUrlinie()
XW.startPart()
MI.startTimer()
#while True:
#   pitch_target = UL.lastNoteFromScale([0, 2, 4, 5, 7, 9, 11]) # testing with a C Major scale
#   print UL.newUrlinieWithDegreeTarget(pitch_target)
#   sleep(1.0)

#HS = HarmonicStructure('SatinDoll.txt')
#while True:
#   HS.Tap()
#   sleep(0.4)
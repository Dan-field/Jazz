from HarmonicStructure import *
from MIDIInput import *
from Urlinie import *
from NoteSender import *
from MusicXMLWriter import *
from Player import *
from TimeKeeper import *
from time import sleep

UL = Urlinie()
NS = NoteSender()
XW = MusicXMLWriter()
LS = HarmonicStructure("Autumn.txt")
MI = MIDIInput()
PP = Player()
TK = TimeKeeper()
MI.setUrlinieReference(UL)
MI.setLeadSheetReference(LS)
MI.setXMLWriterReference(XW)
MI.setPlayerReference(PP)
MI.setTimeKeeperReference(TK)
#UL.setMIDIInputReference(MI)
#UL.setLeadSheetReference(LS)
#UL.setNoteSenderReference(NS)
LS.setUrlinieReference(UL)
LS.setPlayerReference(PP)
NS.setXMLWriterReference(XW)
PP.setUrlinieReference(UL)
PP.setNoteSenderReference(NS)
PP.setLeadSheetReference(LS)
PP.setMIDIInputReference(MI)
TK.setLeadSheetReference(LS)
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
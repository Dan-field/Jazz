from time import sleep
from music import *
from gui import *

tempo = 175
volume = 100
note = 42

d = Display("tapping", 270, 200)
minTempo = 20
maxTempo = 240
startTempo = 120
minVol = 0
maxVol = 127
startVol = volume

label1 = Label("Tempo: "+str(startTempo)+" bpm")
label2 = Label("Vol: "+str(volume))

def setTempo(newTempo):
   global label1, tempo
   tempo = newTempo
   label1.setText("Tempo: "+str(newTempo)+" bpm")
   
def setVolume(newVolume):
   global label2, volume
   volume = newVolume
   label2.setText("Vol: "+str(newVolume))
   
slider1 = Slider(HORIZONTAL, minTempo, maxTempo, startTempo, setTempo)
slider2 = Slider(HORIZONTAL, minVol, maxVol, startVol, setVolume)

d.add(label1, 40, 30)
d.add(slider1, 40, 60)
d.add(label2, 40, 120)
d.add(slider2, 40, 150)

while(True):
   Play.noteOn(note, volume, 9)
   sleep(60.0/tempo)
   Play.noteOff(note, 9)
   

from time import sleep
from music import *
from gui import *
from random import randint

tempo = 175
volume = 100
label1 = Label("Tempo: "+str(tempo)+" bpm")
label2 = Label("Vol: "+str(volume))
kill = False

def setTempo(newTempo):
   global label1, tempo
   tempo = newTempo
   label1.setText("Tempo: "+str(newTempo)+" bpm")
     
def setVolume(newVolume):
   global label2, volume
   volume = newVolume
   label2.setText("Vol: "+str(newVolume))
   
def killTimer():
   global kill
   kill = True
   
def tap(ls):
   global volume, tempo
   ls.beatCrotchet()
   if ls.getCurrentBeat() == 0:
      print ls.getCurrentChord()
   Play.noteOn(59, volume, 9)
   sleep(10.0/tempo)
   Play.noteOff(59, 9)

def startTimer(ls):

   position = 0
   
   d = Display("tap", 270, 240)
   minTempo = 45
   maxTempo = 290
   startTempo = tempo
   minVol = 0
   maxVol = 127
   startVol = volume
   
   slider1 = Slider(HORIZONTAL, minTempo, maxTempo, startTempo, setTempo)
   slider2 = Slider(HORIZONTAL, minVol, maxVol, startVol, setVolume)
   button1 = Button("kill", killTimer)
      
   d.add(label1, 40, 30)
   d.add(slider1, 40, 60)
   d.add(label2, 40, 120)
   d.add(slider2, 40, 150)
   d.add(button1, 40, 210)
   
   global kill
   # run the central counter
   while(kill == False):
      if ls.getCurrentBar() < ls.getTotalBars():
         tap(ls)
         sleep(60.0/tempo)
      else:
         kill = True
   

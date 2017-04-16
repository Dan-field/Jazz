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

def startTimer(note_list, duration_list):

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
   while(kill == False):
      # add a bit of randomness to the volume
      thisvol = volume + randint(-12, 12)
      if thisvol > 127: thisvol = 127
      if thisvol < 0: thisvol = 0
      # play the next note in the list
      # randomise the held length slightly
      holdpercent = (85 + randint(0,15))/100.0
      Play.noteOn(note_list[position], thisvol, 0)
      sleep(60.0*duration_list[position]*holdpercent/tempo)
      Play.noteOff(note_list[position], 0)
      sleep(60.0*duration_list[position]*(1.0-holdpercent)/tempo)
      if len(note_list)-1 > position:
         position += 1
      else:
         kill = True
   

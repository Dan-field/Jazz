from improfunctions import *
from timerfunction import *
from music import *
import threading

output = Phrase()

# import the chord list and the bar list from file
chords, bars = GetChords('SatinDoll.txt')
beats_per_bar = 4.0 # must be a decimal (not int) since it may be used for division

# Work through one bar at a time
for bar_count, bar in enumerate(bars):
   # get the root notes and durations
   roots, durations = BreakDown(bar, beats_per_bar)
   root_numbers = Octavify(roots, '4') # pass the MIDI octave number as a string
   output.addNoteList(root_numbers, durations)
   print roots, root_numbers, durations
output.setTempo(200)

Play.midi(output)
startTimer()

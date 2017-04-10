from improfunctions import *
from timerfunction import *
from music import *



# import the chord list and the bar list from file
chords, bars = GetChords('SatinDoll.txt')
beats_per_bar = 4.0 # must be a decimal (not int) since it may be used for division

# generate a phrase containing just the roots
root_pitches, root_durations = ExtractRoots(bars, beats_per_bar)

startTimer(root_pitches, root_durations)
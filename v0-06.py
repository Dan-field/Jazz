from timerfunction import *
from music import *
from LeadSheet import *

# use the new LeadSheet class based on the chord chart file
ls = LeadSheet('SatinDoll.txt', 4)
# extract the root pitches and durations from the class object
pitches, durations = ls.GetRoots()
# use the v0.05 startTimer function
startTimer(pitches, durations)
from timerfunction import *
from LeadSheet import *
from ChordWatcher import *
from Analysis import *

# use the new LeadSheet class based on the chord chart file
ls = LeadSheet('SatinDoll.txt', 4)
#Analysis(ls).TwoFiveOne()
# initialise the player
mrPlayer = ChordWatcher(ls)
# start the timer
startTimer(ls, mrPlayer)
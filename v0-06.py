from timerfunction import *
from LeadSheet import *
from RandomPlayer import *

# use the new LeadSheet class based on the chord chart file
ls = LeadSheet('SatinDoll.txt', 4)
# initialise the player
mrPlayer = RandomPlayer(ls)
# start the timer
startTimer(ls, mrPlayer)
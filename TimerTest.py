from midi import *

M = MidiOut()

def loop():
   M.note(80, 0, 120, 70, 0, 64)

T = Timer(1000, loop)
T.start()
from bluebox import DTMF
from bluebox.box import Sequencer

mf = DTMF()
seq = Sequencer(mf = mf, length = 100.0)

seq.length = 100.0
seq('12345')

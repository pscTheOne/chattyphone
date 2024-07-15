from bluebox import DTMF
from bluebox.box import Sequencer

mf = DTMF()
seq = Sequencer(mf = mf)

seq('12345')

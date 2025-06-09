import Ice
import os
SLICE_PATH = os.path.join(os.path.dirname(__file__), '..', 'calculator.ice')
Ice.loadSlice('', ['-I' + Ice.getSliceDir(), SLICE_PATH])
import Calculator

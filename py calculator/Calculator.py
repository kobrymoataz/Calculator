import Ice
import IcePy

# Declare module
_M_Calculator = Ice.openModule("Calculator")

# Define the interface
_M_Calculator.__name__ = "Calculator"

class Service(Ice.Object):
    def ice_ids(self, current=None):
        return ('::Calculator::Service', '::Ice::Object')

    def ice_id(self, current=None):
        return '::Calculator::Service'

    def __str__(self):
        return IcePy.stringify(self, self.ice_id())

    __ice_operations__ = ('div', 'mult', 'sub', 'sum')

    @staticmethod
    def _op_sum():
        return IcePy.Operation(
            'sum',
            Ice.OperationMode.Normal,
            Ice.OperationMode.Normal,
            False,
            None,
            (),
            (((), (), (float, False, 0), (float, False, 0)),),
            (float, False, 0),
            (),
            ()  # ✅ metadata as empty tuple
        )

    @staticmethod
    def _op_sub():
        return IcePy.Operation(
            'sub',
            Ice.OperationMode.Normal,
            Ice.OperationMode.Normal,
            False,
            None,
            (),
            (((), (), (float, False, 0), (float, False, 0)),),
            (float, False, 0),
            (),
            ()
        )

    @staticmethod
    def _op_mult():
        return IcePy.Operation(
            'mult',
            Ice.OperationMode.Normal,
            Ice.OperationMode.Normal,
            False,
            None,
            (),
            (((), (), (float, False, 0), (float, False, 0)),),
            (float, False, 0),
            (),
            ()
        )

    @staticmethod
    def _op_div():
        return IcePy.Operation(
            'div',
            Ice.OperationMode.Normal,
            Ice.OperationMode.Normal,
            False,
            None,
            (),
            (((), (), (float, False, 0), (float, False, 0)),),
            (float, False, 0),
            (),
            ()
        )

    _ice_type = IcePy.declareClass('::Calculator::Service')
    _ice_operations = [_op_div(), _op_mult(), _op_sub(), _op_sum()]

_M_Calculator.Service = Service
Calculator = _M_Calculator

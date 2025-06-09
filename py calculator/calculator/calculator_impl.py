from calculator import calculator_ice
import Calculator
import Ice

class DivisionByZeroError(Ice.UserException):
    def __init__(self, message="Division by zero"):
        self.message = message

class InvalidOperationError(Ice.UserException):
    def __init__(self, message="Invalid operation"):
        self.message = message

class CalculatorI(Calculator.Service):
    def __init__(self):
        self.last_error = None

    def sum(self, op1, op2, current=None):
        self.last_error = None
        try:
            return float(op1 + op2)
        except Exception as e:
            self.last_error = f"Error in sum operation: {str(e)}"
            return float('nan')

    def sub(self, op1, op2, current=None):
        self.last_error = None
        try:
            return float(op1 - op2)
        except Exception as e:
            self.last_error = f"Error in subtraction operation: {str(e)}"
            return float('nan')

    def mult(self, op1, op2, current=None):
        self.last_error = None
        try:
            return float(op1 * op2)
        except Exception as e:
            self.last_error = f"Error in multiplication operation: {str(e)}"
            return float('nan')

    def div(self, op1, op2, current=None):
        self.last_error = None
        try:
            if op2 == 0:
                self.last_error = "division by zero"
                return float('nan')
            return float(op1 / op2)
        except Exception as e:
            self.last_error = f"Error in division operation: {str(e)}"
            return float('nan')
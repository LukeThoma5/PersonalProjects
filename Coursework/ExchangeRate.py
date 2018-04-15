from decimal import *
from LoggableObject import LoggableObject
class ExchangeRate(LoggableObject):

  def __init__(self, A2B, B2A=None):
    super().__init__()
    self.A2B = Decimal(A2B)
    
    # If a valid value for the conversion in the opposite direction
    # is not defined then default it to the inverse of defined conversion
    if B2A is None:
      self.B2A = Decimal(1/self.A2B)
    else:
      self.B2A = Decimal(B2A)
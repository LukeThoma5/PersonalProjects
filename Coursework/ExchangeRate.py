class ExchangeRate:

  def __init__(self, A2B, B2A=None):
    self.A2B = A2B
    self.B2A = B2A
    # If a valid value for the conversion in the opposite direction
    # is not defined then default it to the inverse of defined conversion
    if self.B2A is None:
      self.B2A = 1/self.A2B
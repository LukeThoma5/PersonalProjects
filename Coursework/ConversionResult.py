class ConversionResult:
  def __init__(self, rate, path = [], successful=True):
    self.rate = rate
    self.path = path
    self.value = 0
    self.successful = successful

  def updateValue(self, value):
    self.value = value * self.rate
    return self #Allow chaining of conversion results. Fluent syntax

  def getRateFormatted(self, places=2):
    return round(self.rate, places)

  def getResultFormatted(self, places=2):
    return str(round(self.value, places))

  def getPath(self):
    return ' => '.join(map(lambda x: x.name, self.path))

  def __repr__(self):
    return self.__str__()

  def __str__(self):
    return "<Path: {}, Rate: {}, Success: {}>".format(
      self.getPath(),
      self.getRateFormatted(3),
      self.successful)

  def invert(self):
    self.rate = 1 / self.rate
    self.path.reverse()
   
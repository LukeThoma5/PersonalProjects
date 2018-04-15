from ExchangeRate import ExchangeRate
from LoggableObject import LoggableObject
class NodeLink(LoggableObject):
  def __init__(self, nodeA, nodeB, buying, selling=None):
    super().__init__()
    self.buying = buying
    self.selling = selling
    # If a selling rate is not defined, copy the rate from buying
    if self.selling is None:
      self._copyToSelling()
    self.nodeA = nodeA
    self.nodeB = nodeB
    # Add the links to the nodes so they can navigate the graph
    self.nodeA.addLink(self)
    self.nodeB.addLink(self)

  def _copyToSelling(self):
    # Initialise new exchange rate with values from buying
    self.selling = ExchangeRate(self.buying.A2B, self.buying.B2A)
    
  def getConnectingNode(self, current):
    # If at A, connecting node is B
    if self.nodeA is current:
      return self.nodeB
    return self.nodeA
    
  def getExchangeRate(self, current, selector=lambda x: x.buying):
    # If at A, get the rate from A => B
    # Use the selector to use either the buying or selling rate
    if (self.nodeA is current):
      return selector(self).A2B
    return selector(self).B2A
    
  def containsNode(self, nodeName):
    # If either of the nodes are nodes that are defined before
    return (self.nodeA.name == nodeName or self.nodeB.name == nodeName)

  def _updateLink(self, A, B, A2B, B2A=None, selector=lambda x: x.buying):
    # Pull the exchange rate out
    rate = selector(self)

    # If parameters passed in the correct way round
    if self.nodeA.name == A:
      rate.A2B = A2B
      # Set to inverse if not defined
      if B2A is None:
        rate.B2A = 1/A2B
      else:
        rate.B2A = B2A
    else:
      # If passed in the inverse way
      rate.B2A = A2B
      if B2A is None:
        rate.A2B = 1/A2B
      else:
        rate.A2B = B2A

  def updateLink(self, A, B, buying, selling=None):
    # Update the buying link using the helper
    self._updateLink(A, B, buying.A2B, buying.B2A, lambda x: x.buying)
    if selling is not None:
      # If selling is defined, update it with the passed in values
      self._updateLink(A, B, selling.A2B, selling.B2A, lambda x: x.selling)
    else:
      # Otherwise copy the updated buying rate
      self._copyToSelling()

  def print(self, selector=lambda x: x.buying):
    return "{} => {} : {}".format(self.nodeA.name, self.nodeB.name, selector(self).A2B)
 
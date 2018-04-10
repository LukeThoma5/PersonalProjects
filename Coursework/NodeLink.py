from ExchangeRate import ExchangeRate
class NodeLink:
  def __init__(self, nodeA, nodeB, buying, selling=None):
    self.buying = buying
    self.selling = selling
    if self.selling is None:
      self._copyToSelling()
    self.nodeA = nodeA
    self.nodeB = nodeB
    self.nodeA.addLink(self)
    self.nodeB.addLink(self)

  def _copyToSelling(self):
    self.selling = ExchangeRate(self.buying.A2B, self.buying.B2A)
    
  def getConnectingNode(self, current):
    if (self.nodeA is current):
      return self.nodeB
    return self.nodeA
    
  def getExchangeRate(self, current, selector=lambda x: x.buying):
    if (self.nodeA is current):
      return selector(self).A2B
    return selector(self).B2A
    
  def containsNode(self, nodeName):
    return (self.nodeA.name == nodeName or self.nodeB.name == nodeName)

  def _updateLink(self, A, B, A2B, B2A=None, selector=lambda x: x.buying):
    rate = selector(self)
    if self.nodeA.name == A:
      rate.A2B = A2B
      if B2A is None:
        rate.B2A = 1/A2B
      else:
        rate.B2A = B2A
    else:
      rate.B2A = A2B
      if B2A is None:
        rate.A2B = 1/A2B
      else:
        rate.A2B = B2A

  def updateLink(self, A, B, buying, selling=None):
    self._updateLink(A, B, buying.A2B, buying.B2A, lambda x: x.buying)
    if selling is not None:
      self._updateLink(A, B, selling.A2B, selling.B2A, lambda x: x.selling)
    else:
      self._copyToSelling()

  def print(self, selector=lambda x: x.buying):
    print("{} => {} : {}".format(self.nodeA.name, self.nodeB.name, selector(self).A2B))
 
class NodeLink:
  def __init__(self, nodeA, nodeB, A2B, B2A=None):
    self.A2B = A2B
    if B2A is None:
      self.B2A = 1 / self.A2B
    else:
      self.B2A = B2A
    self.nodeA = nodeA
    self.nodeB = nodeB
    self.nodeA.addLink(self)
    self.nodeB.addLink(self)
    
  def getConnectingNode(self, current):
    if (self.nodeA is current):
      return self.nodeB
    return self.nodeA
    
  def getExchangeRate(self, current):
    if (self.nodeA is current):
      return self.A2B
    return self.B2A
    
  def containsNode(self, nodeName):
    return self.nodeA.name == nodeName or self.nodeB.name == nodeName

  def print(self):
    print("{} => {} : {}".format(self.nodeA.name, self.nodeB.name, self.A2B))
 
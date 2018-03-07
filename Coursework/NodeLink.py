class NodeLink:
  def __init__(this, value, nodeA, nodeB):
    this.value = value;
    this.nodeA = nodeA;
    this.nodeB = nodeB;
    this.nodeA.addLink(this);
    this.nodeB.addLink(this);
    
  def getConnectingNode(this, current):
    if (this.nodeA is current):
      return this.nodeB;
    return this.nodeA;
    
  def getExchangeRate(this, current):
    if (this.nodeA is current):
      return this.value;
    return 1 / this.value;
    
  def containsNode(this, nodeName):
    return this.nodeA.name == nodeName or this.nodeB.name == nodeName;

  def print(this):
    print("{} => {} : {}".format(this.nodeA.name, this.nodeB.name, this.value))
 
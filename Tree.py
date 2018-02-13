allNodes = [];

class NodeLink:
  def __init__(this, nodeA, nodeB, value):
    print("creating!")
    this.value = value;
    this.nodeA = nodeA;
    this.nodeB = nodeB;
    # nodeA.addLink(this);
    # nodeB.addLink(this);
    
  def getConnectingNode(this, current):
    if (this.nodeA is current):
      return this.nodeB;
    return this.nodeA;
    
  def getExchangeRate(this, current):
    if (this.nodeA is current):
      return value;
    return 1 / value;
    
  def addLinks(this):
    this.nodeA.addLink(this);
    # this.nodeB.addLink(this);
    
  def containsNode(this, nodeName):
    return this.nodeA.name == nodeName or this.nodeB.name == nodeName;
  
class Node:
  
  def __init__(this, name = "", nodes=[]):
    this.name = name;
    this.nodes = nodes;
    
  def addNode(this, nodeName, value):
    for node in allNodes:
      if node.name == nodeName:
        print("found", nodeName)
        NodeLink(this, node, value).addLinks();
        
  def addLink(this, link):
    print("Adding", link, "to", this.name)
    this.nodes.append(link);
    
  def getExchangeRate(this, nodeName):
    for link in this.nodes:
      if link.containsNode(nodeName) == nodeName:
        return link.getExchangeRate(this);
    return -1;
        
    
  def print(this):
      print("-"*30);
      print(this.name, ":");
      print(this.nodes);
      for link in this.nodes:
        print(link);
        print("   ", link.getConnectingNode(this).name);
        

allNodes.append(Node("A"));
allNodes.append(Node("B"));
allNodes.append(Node("C"));
allNodes.append(Node("D"));

allNodes[0].addNode("C", 10);
allNodes[0].addNode("D", 15);
allNodes[1].addNode("C", 10);

print(allNodes[0].getExchangeRate("C"))

allNodes[0].print();
allNodes[2].print();

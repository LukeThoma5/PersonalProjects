class Node:
  
  def __init__(this, graph, name = ""):
    this.graph = graph;
    this.name = name;
    this.nodes = [];
        
  def addLink(this, link):
    this.nodes.append(link);
    
  def getExchangeRate(this, nodeName):
    for link in this.nodes:
        if link.containsNode(nodeName):
            return link.getExchangeRate(this);
        print("not found");
    return -1;
    
  def print(this):
      print("-"*30);
      print(this.name, ":");
      print(this.nodes);
      for link in this.nodes:
        print(link);
        print("   ", link.getConnectingNode(this).name);
        

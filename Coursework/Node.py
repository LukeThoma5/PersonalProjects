class Node:
  
  def __init__(self, graph, name = ""):
    self.graph = graph
    self.name = name
    self.nodes = []
        
  def addLink(self, link):
    self.nodes.append(link)
    
  def getExchangeRate(self, nodeName):
    for link in self.nodes:
        if link.containsNode(nodeName):
            return link.getExchangeRate(self)
        print("not found")
    return -1
    
  def print(self):
      print("-"*30)
      print(self.name, ":")
      print(self.nodes)
      for link in self.nodes:
        print(link)
        print("   ", link.getConnectingNode(self).name)
        

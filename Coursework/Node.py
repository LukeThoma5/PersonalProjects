class Node:
  
  def __init__(self, graph, name = ""):
    self.graph = graph
    self.name = name
    self.nodes = []
        
  def addLink(self, link):
    self.nodes.append(link)
    
  def getExchangeRate(self, nodeName, selector):
    for link in self.nodes:
        if link.containsNode(nodeName):
            return link.getExchangeRate(self, selector)
        print("not found")
    return -1

  def hasLink(self, nodeName):
    for link in self.nodes:
        if link.containsNode(nodeName):
          return True
    return False

  def updateLink(self, nodeName, A2B, B2A=None):
    for link in self.nodes:
        if link.containsNode(nodeName):
          print("found link")
          link.updateLink(self.name, nodeName, A2B, B2A)

    
  def print(self):
      print("-"*30)
      print(self.name, ":")
      print(self.nodes)
      for link in self.nodes:
        print(link)
        print("   ", link.getConnectingNode(self).name)
        

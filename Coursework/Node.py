class Node:
  
  def __init__(self, name = ""):
    self.name = name
    self.nodes = []
        
  def addLink(self, link):
    # Push the NodeLink object into the list of nodes
    self.nodes.append(link)
    
  def getExchangeRate(self, nodeName, selector):
    for link in self.nodes:
      # If the node we are looking for
      if link.containsNode(nodeName):
        # Return its exchange rate
        return link.getExchangeRate(self, selector)
    # Return unsuccessful
    return -1

  def hasLink(self, nodeName):
    for link in self.nodes:
      if link.containsNode(nodeName):
        return True
    return False

  def updateLink(self, nodeName, A2B, B2A=None):
    # Find the link with the corresponding node,
    # Then update the value
    for link in self.nodes:
      if link.containsNode(nodeName):
        link.updateLink(self.name, nodeName, A2B, B2A)
 
  def print(self):
    print("-"*30)
    print(self.name, ":")
    print(self.nodes)
    for link in self.nodes:
      print(link)
      print("   ", link.getConnectingNode(self).name)
        

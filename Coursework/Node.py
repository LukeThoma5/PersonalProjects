from LoggableObject import LoggableObject
class Node(LoggableObject):

  def __init__(self, name = ""):
    super().__init__()
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

  def updateLink(self, nodeName, Buying, Selling=None):
    # Find the link with the corresponding node,
    # Then update the value
    for link in self.nodes:
      if link.containsNode(nodeName):
        link.updateLink(self.name, nodeName, Buying, Selling)
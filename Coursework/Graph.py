import numpy as np
import matplotlib.pyplot as plt
from ConversionResult import ConversionResult
from NodeLink import NodeLink, buying_selector, selling_selector
from ExchangeRate import ExchangeRate
from Node import Node
from LoggableObject import LoggableObject
import pickle
import csv

FILE_LOCATION = "exchangeRates.bin"
DUMMY_NAME = "DUMMY"
class Graph(LoggableObject):
    
  def __init__(self):
    super().__init__()
    # Dictionary of node names (USD, GBP ect)
    # To Node Objects
    self.allNodes = {}
    
  def save(self, location=FILE_LOCATION):
    # Open the file and save the state of the graph
    with open(location, "wb") as binaryFile:
      pickle.dump(self, binaryFile)
        
  def addNode(self, name):
    if not self.nodeExists(name):
      self.allNodes[name] = Node(name)

  def nodeExists(self, name):
    # If in the list of nodes then it exists
    if name in self.allNodes.keys():
      return True
    return False
        
  def getNode(self, name):
    # Thin wrapper to encapsulate all Nodes
    try:
      return self.allNodes[name]
    except:
      return Node(DUMMY_NAME)
    
  def addLink(self, nameA, nameB, buying, selling=None):
    # Get the nodes out
    nodeA = self.getNode(nameA)
    nodeB = self.getNode(nameB)
    if nodeA.name == DUMMY_NAME or nodeB.name == DUMMY_NAME:
      return
    # If a link exists update it, otherwise create a new one
    if not nodeA.hasLink(nameB):
      NodeLink(nodeA, nodeB, buying, selling)
    else:
      nodeA.updateLink(nameB, buying, selling)
        
  def getExchangeRate(self, nameA, nameB, selector):
    # Get the node for A and then get the exchange rate to get to B
    return self.getNode(nameA).getExchangeRate(nameB, selector)
  
  def getExchangeRateBest(self, nameA, nameB, selector):
    # Get the nodes out
    start = self.getNode(nameA)
    destination = self.getNode(nameB)
    # Get the best exhange rate by finding all routes between destination
    # And return the best one
    return self.getExchangeRateRec(start, destination, [], selector)
  
  def getAllRates(self, fromNode, destination, attendedNodes, selector):
    attendedNodes.append(fromNode) # We have attended this node
    conversions = [] # Initialise an empty list for the conversions
    for link in fromNode.nodes: # For every node the start is connected to
      current = link.getConnectingNode(fromNode) # Get which node its connected to
      if current is destination: # If at the destination
        # Append the direct exchange rate, the route is only fromNode => destination
        conversions.append(ConversionResult(fromNode.getExchangeRate(destination.name, selector), [fromNode, destination]))
      else:
        # If not the destination, try and get from the new current node to the destination
        if current in attendedNodes: # If we've already visited this node, skip it to prevent infinite loops
          continue
        # Make a local copy of the attendedNodes
        # A list slice forces a new list to be created with the same elements
        # Otherwise only full one branch would be visited
        nodes = attendedNodes[:]
        # We've visited the current node so mark it as visited
        nodes.append(current)
        # Get the exchange rate from fromNode => current node
        directConversion = fromNode.getExchangeRate(current.name, selector)
        # Get the exchange rate from current node => destination
        # Don't visit any nodes we've already visited by ignoring the nodes in nodes list
        tailConversion = self.getExchangeRateRec(current, destination, nodes, selector)
        # If we were able to get from current node to the destination,
        # add the conversion to the list of possible conversions
        if tailConversion.successful:
          path = [fromNode] # Initialise the path as the fromNode
          path.extend(tailConversion.path) # Add all the nodes visited while going current => destination
          # The conversion is the combination of the direct conversion (fromNode => current) and tail conversion (current => destination)
          conversion = ConversionResult(directConversion * tailConversion.rate, path)
          conversions.append(conversion) # Add the conversion
    
    # Sort the conversions by descending rate, so best rate is first
    conversions.sort(key=lambda conversion: conversion.rate, reverse=True)
    return conversions
  
  def getExchangeRateRec(self, fromNode, destination, attendedNodes, selector):
    # Get all the valid routes from the fromNode to the destination
    conversions = self.getAllRates(fromNode, destination, attendedNodes, selector)
    
    # If we have a valid conversion,
    # Return the first one as they are sorted by best rate
    if len(conversions) > 0:
      return conversions[0]

    # If no conversions then return unsuccessful
    return ConversionResult(-1, [], successful=False)
  
  def getGraphData(self, currency, selector):
    plotsOfPlots = [] # List of currencies conversion rates
    labels = [] # currency names
    start = self.getNode(currency) # the currency we're graphing
    keys = list(self.allNodes.keys())
    keys.sort()
    for comparison in keys: # For all currencies
      if comparison == currency: # Don't plot against yourself
        continue
      comp = self.getNode(comparison) # Get the node we're currently graphing against
      # Get all the rates to go from the start to the node we're currently plotting
      # It's a list of ConversionResult objects, will map to just sucessful rates
      conversions = self.getAllRates(start, comp, [], selector)

      graphData = [] # List of successful conversions
      for conversion in conversions: 
        if conversion.successful: # Only add if was successful
          graphData.append(float(conversion.rate))
      plotsOfPlots.append(graphData) # Add the list of conversions 
      labels.append(comparison) # Add which conversion its for

    return (plotsOfPlots, labels) # Return a tuple of the values and labels
    

  def plotGraph(self, currency, selector):
    # Get all the successful conversions
    plotsOfPlots, labels = self.getGraphData(currency, selector)
    fig, ax = plt.subplots()
    # Create a boxplot with the various currencies
    plt.boxplot(plotsOfPlots, labels=labels)
    # Show the plit
    plt.show()

  def getAllCurrencies(self):
    # Helper function for getting at the list of currencies to load into a drop down
    return self.allNodes.keys()

  def generateBuySellData(self, currency, delegate):
    buying = []
    selling = []
    currencies = []
    for comparison in self.allNodes.keys():
      if comparison == currency:
        continue
      b = float(delegate(self, currency, comparison, buying_selector))
      s = float(delegate(self, currency, comparison, selling_selector))
      if b > 0 and s > 0:
        buying.append(round(b, 3))
        selling.append(round(s, 3))
        currencies.append(comparison)
    return (buying, selling, currencies)

  def plotBuyVsSell(self, currency, delegate, name):
    buying, selling, currencies = self.generateBuySellData(currency, delegate)
    fig, ax = plt.subplots()
    ind = np.arange(len(buying))  # the x locations for the groups
    width = 0.35  # the width of the bars
    rects1 = ax.bar(ind - width/2, buying, width,
                color='SkyBlue', label='Buying')
    rects2 = ax.bar(ind + width/2, selling, width,
                color='IndianRed', label='Selling')
    ax.set_ylabel('Rate')
    ax.set_title('Buying and selling Rates of {} using {}'.format(currency, name))
    ax.set_xticks(ind)
    ax.set_xticklabels(currencies)
    ax.legend()

    plt.show()



  def calcRouteMatrix(self, delegate, selector):
    matrix = [] # The CSV data
    keys = list(self.allNodes.keys())
    keys.sort()
    for currentNode in keys: # For all nodes create a row
      conversions = []
      for comparisonNode in keys: # for all nodes find a conversion
        if (currentNode == comparisonNode): # If yourself define as -1
          conversion = str(-1)
        else: # Otherwise find the conversion using the passed in function
          conversion = delegate(self, currentNode, comparisonNode, selector)
        conversions.append(conversion)
      matrix.append(conversions) # Allways add a conversion, unsuccessful ones are -1
    return matrix

  def exportRates(self, best, path, selector):
    if best:
      delegate = matrixBest # Set the delegate to the matrixBest function
    else:
      # Otherwise only get direct conversions, -1 for all else
      delegate = matrixDirect
    # Get the matrix data
    matrix = self.calcRouteMatrix(delegate, selector)
    prettyKeys = [" "] # First cell of the csv is blank
    keys = list(self.allNodes.keys()) # All the currencies
    keys.sort()
    prettyKeys.extend(keys) # add all the currencies 
    with open(path, 'w', newline='') as csvfile:
      writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL) # Open the csv file
      writer.writerow(prettyKeys) # Write the header line
      for index, conversions in enumerate(matrix): # For each line of conversions
        currency = keys[index] # Get the currency code
        row = [currency] # Initialise the row as the currency code
        row.extend(conversions) # Add the exchange rates to the row
        writer.writerow(row) # Write the row to the file
      

def matrixBest(graph, currentNode, comparisonNode, selector):
  # Get the best exchange rates, replace unsuccessful with -1
  result = graph.getExchangeRateBest(currentNode, comparisonNode, selector)
  if (result.successful):
    return str(result.rate)
  return str(-1)

def matrixDirect(graph, currentNode, comparisonNode, selector):
  # Get direct exchange rates, unsuccessful are -1
  return str(graph.getExchangeRate(currentNode, comparisonNode, selector))

def generateDemoGraph():
  graph = Graph()
  for name in ["GBP", "USD", "EURO", "TEST", "YEN"]:
      graph.addNode(name)
      
  graph.addLink("GBP", "USD", ExchangeRate(1.6, 1.5), ExchangeRate(1.4, 0.8))
  graph.addLink("USD", "EURO", ExchangeRate(1.2))
  graph.addLink("EURO", "YEN", ExchangeRate(1.4, 0.7), ExchangeRate(1.3, 0.9))
  graph.addLink("TEST", "YEN", ExchangeRate(2), ExchangeRate(1, 0.6))
  graph.addLink("GBP", "TEST", ExchangeRate(0.2, 0.2), ExchangeRate(0.15, 0.15))
  graph.addLink("USD", "YEN", ExchangeRate(0.5, 1.25))
  return graph

if __name__ == "__main__":
  graph = generateDemoGraph()
  graph.plotBuyVsSell("USD", matrixBest, "Best Match")
  graph.plotBuyVsSell("USD", matrixDirect, "Direct Only")
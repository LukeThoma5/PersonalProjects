import pickle;
import numpy as np;
import matplotlib.pyplot as plt;

FILE_LOCATION = "exchangeRates.bin";

class Graph:
    
  def __init__(this):
    this.allNodes = {};
    
  def save(this):
    pickle.dump(this, open(FILE_LOCATION, "wb"))
        
  def addNode(this, name):
    this.allNodes[name] = Node(this, name);
        
  def getNode(this, name):
    return this.allNodes[name];
    
  def addLink(this, nameA, nameB, value):
    nodeA = this.getNode(nameA);
    nodeB = this.getNode(nameB);
    NodeLink(value, nodeA, nodeB);
        
  def getExchangeRate(this, nameA, nameB):
    return this.getNode(nameA).getExchangeRate(nameB);
  
  def getExchangeRateBest(this, nameA, nameB):
    start = this.getNode(nameA);
    destination = this.getNode(nameB);
    return this.getExchangeRateRec(start, destination, []);
  
  def getAllRates(this, fromNode, destination, attendedNodes = []):
    attendedNodes.append(fromNode);
    conversions = [];
    for link in fromNode.nodes:
      current = link.getConnectingNode(fromNode)
      if (current is destination):
        conversions.append(ConversionResult(fromNode.getExchangeRate(destination.name), [fromNode, destination]));
      else:
        if (current in attendedNodes):
          continue;
        nodes = attendedNodes[:]
        nodes.append(current);
        directConversion = fromNode.getExchangeRate(current.name);
        tailConversion = this.getExchangeRateRec(current, destination, nodes);
        if (tailConversion.successful):
          path = [fromNode];
          path.extend(tailConversion.path);
          conversion = ConversionResult(directConversion * tailConversion.rate, path);
          conversions.append(conversion);
    conversions.sort(key=lambda conversion: conversion.rate, reverse=True);
    return conversions;
  
  def getExchangeRateRec(this, fromNode, destination, attendedNodes = []):
    conversions = this.getAllRates(fromNode, destination, attendedNodes);
    
    if len(conversions) > 0:
      return conversions[0];
  
    print("WARNING: INVALID ROUTE", fromNode.name, destination.name);
    return ConversionResult(-1, [], successful=False);
  
  def getGraphData(this, currency):
    plotsOfPlots = [];
    labels = [];
    start = this.getNode(currency);
    for comparison in this.allNodes.keys():
      if comparison == currency:
        continue;
      comp = this.getNode(comparison)
      conversions = this.getAllRates(start, comp, []);
      graphData = [];
      print(start.name, comp.name, conversions);
      for conversion in conversions:
        if (conversion.successful):
          graphData.append(conversion.rate)
      plotsOfPlots.append(graphData);
      labels.append(comparison);

    fig, ax = plt.subplots();
    plt.boxplot(plotsOfPlots, labels=labels);
    plt.show();
    
  def printAllGraphs(this):
    for nodeKey in this.allNodes.keys():
      this.getGraphData(nodeKey)
        

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
    
class ConversionResult:
  def __init__(this, rate, path = [], successful=True):
    this.rate = rate;
    this.path = path;
    this.value = 0;
    this.successful = successful;

  def updateValue(this, value):
    this.value = value * this.rate;
    return this; #Allow chaining of conversion results. Fluent syntax

  def getRateFormatted(this, places=2):
    return round(this.rate, places);

  def getResultFormatted(this, places=2):
    return round(this.value, places);

  def getPath(this):
    return ' => '.join(map(lambda x: x.name, this.path));

  def __repr__(this):
    return this.__str__();

  def __str__(this):
    return "<Path: {}, Rate: {}, Success: {}>".format(
      this.getPath(),
      this.getRateFormatted(3),
      this.successful);

    def invert(this):
        this.rate = 1 / this.rate;
        this.path.reverse();
        

  
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
        

def makeGraph():
  print("Making Graph");
  graph = Graph();
  for name in ["GBP", "USD", "EURO", "TEST", "YEN"]:
      graph.addNode(name);
      
  graph.addLink("GBP", "USD", 1.6);
  graph.addLink("USD", "EURO", 1.2);
  graph.addLink("EURO", "YEN", 1.4);
  graph.addLink("TEST", "YEN", 2);
  graph.addLink("GBP", "TEST", 2.4);
  graph.addLink("USD", "YEN", 0.5);
  return graph

def main():
  try:
    graph = pickle.load(open(FILE_LOCATION, "rb"))
  except:
    graph = makeGraph()  
  
  #print(graph.getExchangeRateBest("USD", "YEN"));
  print(graph.getExchangeRateBest("GBP", "YEN"))
  
  
  #graph.getGraphData("USD");
  graph.printAllGraphs();
  graph.save();
  
if __name__ == "__main__":
  main()
  
import numpy as np;
import matplotlib.pyplot as plt;
from ConversionResult import ConversionResult;
from NodeLink import NodeLink;
from Node import Node;
import pickle;

FILE_LOCATION = "exchangeRates.bin"; 
class Graph:
    
  def __init__(self):
    self.allNodes = {};
    
  def save(self):
    pickle.dump(self, open(FILE_LOCATION, "wb"))
        
  def addNode(self, name):
    self.allNodes[name] = Node(self, name);
        
  def getNode(self, name):
    return self.allNodes[name];
    
  def addLink(self, nameA, nameB, value):
    nodeA = self.getNode(nameA);
    nodeB = self.getNode(nameB);
    NodeLink(value, nodeA, nodeB);
        
  def getExchangeRate(self, nameA, nameB):
    return self.getNode(nameA).getExchangeRate(nameB);
  
  def getExchangeRateBest(self, nameA, nameB):
    start = self.getNode(nameA);
    destination = self.getNode(nameB);
    return self.getExchangeRateRec(start, destination, []);
  
  def getAllRates(self, fromNode, destination, attendedNodes = []):
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
        tailConversion = self.getExchangeRateRec(current, destination, nodes);
        if (tailConversion.successful):
          path = [fromNode];
          path.extend(tailConversion.path);
          conversion = ConversionResult(directConversion * tailConversion.rate, path);
          conversions.append(conversion);
    conversions.sort(key=lambda conversion: conversion.rate, reverse=True);
    return conversions;
  
  def getExchangeRateRec(self, fromNode, destination, attendedNodes = []):
    conversions = self.getAllRates(fromNode, destination, attendedNodes);
    
    if len(conversions) > 0:
      return conversions[0];
  
    print("WARNING: INVALID ROUTE", fromNode.name, destination.name);
    return ConversionResult(-1, [], successful=False);
  
  def getGraphData(self, currency):
    plotsOfPlots = [];
    labels = [];
    start = self.getNode(currency);
    for comparison in self.allNodes.keys():
      if comparison == currency:
        continue;
      comp = self.getNode(comparison)
      conversions = self.getAllRates(start, comp, []);
      graphData = [];
      print(start.name, comp.name, conversions);
      for conversion in conversions:
        if (conversion.successful):
          graphData.append(conversion.rate)
      plotsOfPlots.append(graphData);
      labels.append(comparison);

    return (plotsOfPlots, labels);
    

  def plotGraph(self, currency):
    plotsOfPlots, labels = self.getGraphData(currency);
    fig, ax = plt.subplots();
    plt.boxplot(plotsOfPlots, labels=labels);
    plt.show();
    
  def printAllGraphs(self):
    for nodeKey in self.allNodes.keys():
      self.plotGraph(nodeKey)

  def getAllCurrencies(self):
    return self.allNodes.keys()
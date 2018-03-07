import numpy as np;
import matplotlib.pyplot as plt;
from ConversionResult import ConversionResult;
from NodeLink import NodeLink;
from Node import Node;
import pickle;

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
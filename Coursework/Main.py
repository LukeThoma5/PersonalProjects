import pickle;
from Graph import Graph, FILE_LOCATION;

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
  
import pickle
from Graph import Graph, FILE_LOCATION
from ExchangeRate import ExchangeRate
from EventHandler import EventHandler
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Converter:
  def __init__(self):
    try:
      self.graph = pickle.load(open(FILE_LOCATION, "rb"))
    except:
      self.graph = generateDemoGraph()  

    self.builder = Gtk.Builder()
    self.builder.add_from_file("MainScreen.glade")
    self.builder.connect_signals(EventHandler(self.graph, self))
    self.MainWindow = self.builder.get_object("MainWindow")
    self.LoginWindow = self.builder.get_object("LoginWindow")
    self.ConversionWindow = self.builder.get_object("ConversionWindow")
    self.AdminWindow = self.builder.get_object("AdminWindow")
    self.LoginWindow.show_all()

  def run(self):
    Gtk.main()

def main():
  converter = Converter()
  converter.run()

def generateDemoGraph():
  graph = Graph()
  for name in ["GBP", "USD", "EURO", "TEST", "YEN"]:
      graph.addNode(name)
      
  graph.addLink("GBP", "USD", ExchangeRate(1.6))
  graph.addLink("USD", "EURO", ExchangeRate(1.2))
  graph.addLink("EURO", "YEN", ExchangeRate(1.4))
  graph.addLink("TEST", "YEN", ExchangeRate(2))
  graph.addLink("GBP", "TEST", ExchangeRate(2.4))
  graph.addLink("USD", "YEN", ExchangeRate(0.5))
  return graph
  
if __name__ == "__main__":
  main()
  
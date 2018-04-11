import pickle
from Graph import Graph, FILE_LOCATION, generateDemoGraph
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


  
if __name__ == "__main__":
  main()
  
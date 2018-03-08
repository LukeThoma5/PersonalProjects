import pickle;
from Graph import Graph, FILE_LOCATION;
import gi;
gi.require_version('Gtk', '3.0');
from gi.repository import Gtk;

class Converter:
  def __init__(self):
    try:
      self.graph = pickle.load(open(FILE_LOCATION, "rb"))
    except:
      self.graph = self.makeGraph()  
    
    #print(graph.getExchangeRateBest("USD", "YEN"));
    print(self.graph.getExchangeRateBest("GBP", "YEN"))

    self.builder = Gtk.Builder()
    self.builder.add_from_file("MainScreen.glade")
    self.builder.connect_signals(MainHandler(self.graph, self))
    self.MainWindow = self.builder.get_object("MainWindow")
    self.ConversionWindow = self.builder.get_object("ConversionWindow")
    self.MainWindow.show_all()
    
    #Gtk.main()
    self.graph.getAllCurrencies();
    
    #graph.getGraphData("USD");
    # graph.printAllGraphs();
    self.graph.save();

  def run(self):
    Gtk.main();
  
  def makeGraph(self):
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
    self.graph = graph;

class MainHandler:
  def __init__(self, graph, converter):
    self.graph = graph;
    self.converter = converter;

  def onDeleteWindow(self, *args):
    Gtk.main_quit(*args);

  def MW_MAKE_EXCHANGE_CLICK(self, button):
    print("Make Exchange");
    
    self.converter.ConversionWindow.show_all();

  def MW_QUIT_CLICK(self, button):
    print("QUIT")
    self.graph.save();
    self.onDeleteWindow();

  def MW_ADMIN_CLICK(self, button):
    print("ADMIN")
  
  def CURRENCY_FROM_ON_LOAD(self, combo, box):
    print("hello", combo, box)
    currencies = self.graph.getAllCurrencies();
    for currency in currencies:
      combo.append_text(currency);

  def LOAD_CURRENCIES(self, button):
    combo_to = self.converter.builder.get_object("CURRENCY_TO");
    combo_from = self.converter.builder.get_object("CURRENCY_FROM");
    currencies = self.graph.getAllCurrencies();
    print(currencies);
    for currency in currencies:
      combo_to.append_text(currency);
      combo_from.append_text(currency);
    button.hide();

  def CONVERT(self, button):
    toC = self.converter.builder.get_object("CURRENCY_TO").get_active_text();
    fromC = self.converter.builder.get_object("CURRENCY_FROM").get_active_text();
    if fromC is None or toC is None:
      return;
    amount = self.converter.builder.get_object("CURRENCY_AMOUNT").get_text();
    conversionResult = self.graph.getExchangeRateBest(fromC, toC);
    conversionResult.updateValue(float(amount));
    self.converter.builder.get_object("CONVERSION_RESULT").get_buffer().set_text(conversionResult.getResultFormatted())
    self.converter.builder.get_object("CONVERSION_EXPLAIN").get_buffer().set_text(conversionResult.__str__())
    


def main():
  converter = Converter();
  converter.run();

  
if __name__ == "__main__":
  main()
  
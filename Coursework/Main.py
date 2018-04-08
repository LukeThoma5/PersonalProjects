import pickle
from Graph import Graph, FILE_LOCATION
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Converter:
  def __init__(self):
    try:
      self.graph = pickle.load(open(FILE_LOCATION, "rb"))
    except:
      self.graph = self.makeGraph()  
    
    #print(graph.getExchangeRateBest("USD", "YEN"))
    print(self.graph.getExchangeRateBest("GBP", "YEN"))

    self.builder = Gtk.Builder()
    self.builder.add_from_file("MainScreen.glade")
    self.builder.connect_signals(MainHandler(self.graph, self))
    self.MainWindow = self.builder.get_object("MainWindow")
    self.LoginWindow = self.builder.get_object("LoginWindow")
    self.ConversionWindow = self.builder.get_object("ConversionWindow")
    self.AdminWindow = self.builder.get_object("AdminWindow")
    self.LoginWindow.show_all()

  def run(self):
    Gtk.main()
  
  def makeGraph(self):
    print("Making Graph")
    graph = Graph()
    for name in ["GBP", "USD", "EURO", "TEST", "YEN"]:
        graph.addNode(name)
        
    graph.addLink("GBP", "USD", 1.6)
    graph.addLink("USD", "EURO", 1.2)
    graph.addLink("EURO", "YEN", 1.4)
    graph.addLink("TEST", "YEN", 2)
    graph.addLink("GBP", "TEST", 2.4)
    graph.addLink("USD", "YEN", 0.5)
    return graph

class MainHandler:
  def __init__(self, graph, converter):
    self.graph = graph
    self.converter = converter

  def get(self, obj):
    return self.converter.builder.get_object(obj)

  def onDeleteWindow(self, *args):
    print("deleting window")
    # Gtk.main_quit(*args)

  def MW_MAKE_EXCHANGE_CLICK(self, button):
    print("Make Exchange")
    
    self.converter.ConversionWindow.show_all()

  def attempt_login(self, button):
    username = self.converter.builder.get_object("USERNAME").get_text()
    password = self.converter.builder.get_object("PASSWORD").get_text()
    if username == "admin" and password == "admin":
      self.converter.MainWindow.show_all()
      self.converter.builder.get_object("BTN_MW_ADMIN").show()
      self.converter.LoginWindow.destroy()

  def guest_login(self, button):
    self.converter.MainWindow.show_all()
    self.converter.builder.get_object("BTN_MW_ADMIN").hide()
    self.converter.LoginWindow.destroy()

  def MW_QUIT_CLICK(self, button):
    print("QUIT")
    self.graph.save()
    self.onDeleteWindow()
    Gtk.main_quit()

  def MW_ADMIN_CLICK(self, button):
    print("ADMIN")
    self.converter.AdminWindow.show_all()

  def export_rates(self, _):
    self.graph.exportRates(False, "rates.direct.csv")

  def export_best_rates(self, _):
    self.graph.exportRates(True, "rates.indirect.csv")
  
  def CURRENCY_FROM_ON_LOAD(self, combo):
    print("hello", combo)
    currencies = self.graph.getAllCurrencies()
    for currency in currencies:
      combo.append_text(currency)

  # def LOAD_CURRENCIES(self, button):
  #   combo_to = self.converter.builder.get_object("CURRENCY_TO")
  #   combo_from = self.converter.builder.get_object("CURRENCY_FROM")
  #   currencies = self.graph.getAllCurrencies()
  #   print(currencies)
  #   for currency in currencies:
  #     combo_to.append_text(currency)
  #     combo_from.append_text(currency)
  #   button.hide()

  def CONVERT(self, button):
    toC = self.converter.builder.get_object("CURRENCY_TO").get_active_text()
    fromC = self.converter.builder.get_object("CURRENCY_FROM").get_active_text()
    if fromC is None or toC is None:
      return
    amount = self.converter.builder.get_object("CURRENCY_AMOUNT").get_text()
    conversionResult = self.graph.getExchangeRateBest(fromC, toC)
    conversionResult.updateValue(float(amount))
    self.converter.builder.get_object("CONVERSION_RESULT").get_buffer().set_text(conversionResult.getResultFormatted())
    self.converter.builder.get_object("CONVERSION_EXPLAIN").get_buffer().set_text(conversionResult.__str__())
  
  def on_new_currency_button_clicked(self, button):
    codeObj = self.get("new_currency_entry")
    code = codeObj.get_text().upper()
    if not self.graph.nodeExists(code):
      self.graph.addNode(code)
      codeObj.set_text("")
      self.get("CURRENCY_FROM_ADMIN").append_text(code)
      self.get("CURRENCY_TO_ADMIN").append_text(code)
  
  def update_rate_button_clicked(self, button):
    A2B = self.converter.builder.get_object("A2B_RATE").get_text()
    B2A = self.converter.builder.get_object("B2A_RATE").get_text()
    if B2A is not None:
      B2A = float(B2A)
    A = self.converter.builder.get_object("CURRENCY_FROM_ADMIN").get_active_text()
    B = self.converter.builder.get_object("CURRENCY_TO_ADMIN").get_active_text()
    self.graph.addLink(A, B, float(A2B), B2A)


def main():
  converter = Converter()
  converter.run()

  
if __name__ == "__main__":
  main()
  
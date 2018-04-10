import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from ExchangeRate import ExchangeRate

class EventHandler:
  def __init__(self, graph, converter):
    self.graph = graph
    self.converter = converter

  def get(self, obj):
    return self.converter.builder.get_object(obj)

  def display_make_exchange(self, _):    
    self.converter.ConversionWindow.show_all()

  def attempt_login(self, _):
    username = self.get("USERNAME").get_text()
    password = self.get("PASSWORD").get_text()
    if username == "admin" and password == "admin":
      self.converter.MainWindow.show_all()
      self.get("BTN_MW_ADMIN").show()
      self.converter.LoginWindow.destroy()

  def guest_login(self, _):
    self.converter.MainWindow.show_all()
    self.get("BTN_MW_ADMIN").hide()
    self.converter.LoginWindow.destroy()

  def quit_program(self, _):
    self.graph.save()
    Gtk.main_quit()

  def display_admin(self, _):
    self.converter.AdminWindow.show_all()

  def export_rates(self, _):
    mode = self.get("conversion_rate_export_selector").get_active_text()
    if "Buying" in mode:
      selector = lambda x: x.buying
    else:
      selector = lambda x: x.selling
    self.graph.exportRates("Best" in mode, "rates.{}.csv".format(mode.replace(" ", "_")), selector)

  
  def combo_box_load_currencies(self, combo):
    print("hello", combo)
    currencies = self.graph.getAllCurrencies()
    for currency in currencies:
      combo.append_text(currency)

  def getSelector(self, option):
    if option == "buying":
      return lambda x: x.buying
    return lambda x: x.selling

  def convert_currency(self, _):
    toC = self.get("CURRENCY_TO").get_active_text()
    fromC = self.get("CURRENCY_FROM").get_active_text()
    mode = self.get("conversion_rate_selector").get_active_text()
    selector = self.getSelector(mode)
    if fromC is None or toC is None:
      return
    amount = self.get("CURRENCY_AMOUNT").get_text()
    conversionResult = self.graph.getExchangeRateBest(fromC, toC, selector)
    conversionResult.updateValue(float(amount))
    self.get("CONVERSION_RESULT").get_buffer().set_text(conversionResult.getResultFormatted())
    self.get("CONVERSION_EXPLAIN").get_buffer().set_text(conversionResult.__str__())
  
  def on_new_currency_button_clicked(self, _):
    codeObj = self.get("new_currency_entry")
    code = codeObj.get_text().upper()
    if not self.graph.nodeExists(code):
      self.graph.addNode(code)
      codeObj.set_text("")
      self.get("CURRENCY_FROM_ADMIN").append_text(code)
      self.get("CURRENCY_TO_ADMIN").append_text(code)
  
  def update_rate_button_clicked(self, _):
    A2B_buy = self.get("A2B_RATE").get_text()
    B2A_buy = self.get("B2A_RATE").get_text()
    A2B_sell = self.get("A2B_RATE_selling").get_text()
    B2A_sell = self.get("B2A_RATE_selling").get_text()
    if B2A_buy is not None:
      B2A_buy = float(B2A_buy)
    if B2A_sell is not None:
      B2A_sell = float(B2A_sell)
    selling = None
    if A2B_sell is not None:
      selling = ExchangeRate(float(A2B_sell), B2A_sell)
    A = self.get("CURRENCY_FROM_ADMIN").get_active_text()
    B = self.get("CURRENCY_TO_ADMIN").get_active_text()
    self.graph.addLink(A, B, ExchangeRate(float(A2B_buy), B2A_buy), selling)

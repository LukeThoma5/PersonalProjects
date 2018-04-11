import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from ExchangeRate import ExchangeRate

class EventHandler:
  def __init__(self, graph, converter):
    self.graph = graph
    self.converter = converter

  def get(self, obj):
    '''Helper function to get a GTK widget'''
    return self.converter.builder.get_object(obj)

  ### <Login Screen> ###
  def attempt_login(self, _):
    username = self.get("USERNAME").get_text()
    password = self.get("PASSWORD").get_text()
    # Only continue if user and password match
    if username == "admin" and password == "admin":
      self.converter.MainWindow.show_all()
      self.get("BTN_MW_ADMIN").show()
      self.converter.LoginWindow.destroy() # Remove the login window

  def guest_login(self, _):
    self.converter.MainWindow.show_all()
    self.get("BTN_MW_ADMIN").hide() # HIide the admin button if not logged in
    self.converter.LoginWindow.destroy()

  ### </Login Screen> ###

  ### <Main Screen> ###
  def quit_program(self, _):
    self.graph.save()
    Gtk.main_quit()

  def display_make_exchange(self, _):    
    self.converter.ConversionWindow.show_all()

  def display_admin(self, _):
    self.converter.AdminWindow.show_all()

  def export_rates(self, _):
    mode = self.get("conversion_rate_export_selector").get_active_text()
    # Select which rate to use from the dropdown text
    if "Buying" in mode:
      selector = lambda x: x.buying
    else:
      selector = lambda x: x.selling
    # Save the rates to file, using the file with the dropdowns text in the filename
    self.graph.exportRates("Best" in mode, "rates.{}.csv".format(mode.replace(" ", "_")), selector)
  ### </Main Screen> ###

  ### <Currency Converter Screen> ###
  def combo_box_load_currencies(self, combo):
    '''On create of the combobox, add all the currencies'''
    currencies = self.graph.getAllCurrencies()
    for currency in currencies:
      combo.append_text(currency)

  def getSelector(self, option):
    if option == "buying":
      return lambda x: x.buying
    return lambda x: x.selling

  def convert_currency(self, _):
    # Get the currencies to convert
    toC = self.get("CURRENCY_TO").get_active_text()
    fromC = self.get("CURRENCY_FROM").get_active_text()
    # Get if its buying or selling
    mode = self.get("conversion_rate_selector").get_active_text()
    # Get the selector function for buying or selling
    selector = self.getSelector(mode)
    if fromC is None or toC is None: # Don't convert if not valid
      return
    amount = self.get("CURRENCY_AMOUNT").get_text() # Get the amount to convert
    conversionResult = self.graph.getExchangeRateBest(fromC, toC, selector) # Get the conversion rate
    conversionResult.updateValue(float(amount)) # Calculate the converted value
    # Show the result
    self.get("CONVERSION_RESULT").get_buffer().set_text(conversionResult.getResultFormatted())
    # Show the explanation of how the rate was selected
    self.get("CONVERSION_EXPLAIN").get_buffer().set_text(conversionResult.__str__())

  ### </Currency Converter Screen> ###
  
  ### <Admin Screen> ###
  def on_new_currency_button_clicked(self, _):
    codeObj = self.get("new_currency_entry") # Get the widget, to get the text and clear when done
    code = codeObj.get_text().upper() # Get the currency code
    if not self.graph.nodeExists(code): # If not in the graph, add it
      self.graph.addNode(code)
      codeObj.set_text("") # Clear to give indication it worked
      # Add new option to the dropdowns
      self.get("CURRENCY_FROM_ADMIN").append_text(code) 
      self.get("CURRENCY_TO_ADMIN").append_text(code)
  
  def update_rate_button_clicked(self, _):
    # Get all the rates
    A2B_buy = self.get("A2B_RATE").get_text()
    B2A_buy = self.get("B2A_RATE").get_text()
    A2B_sell = self.get("A2B_RATE_selling").get_text()
    B2A_sell = self.get("B2A_RATE_selling").get_text()
    # If we have a rate, convert it to float
    if B2A_buy is not None:
      B2A_buy = float(B2A_buy)
    if B2A_sell is not None:
      B2A_sell = float(B2A_sell)
    selling = None # Initialise selling to nothing
    if A2B_sell is not None: # if we have the minimal needed to create an exchange rate
      selling = ExchangeRate(float(A2B_sell), B2A_sell) # Create a selling rate
    # Get the currencies involved
    A = self.get("CURRENCY_FROM_ADMIN").get_active_text()
    B = self.get("CURRENCY_TO_ADMIN").get_active_text()
    # Add or update the link
    self.graph.addLink(A, B, ExchangeRate(float(A2B_buy), B2A_buy), selling)

  ### </Admin Screen> ###

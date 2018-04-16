import inspect

class LoggerSingleton:
  instance = None

  class __Logger:
    def __init__(self):
      self.logs = []
      self.calls = {}

    def log(self, function, location, *args):
      self.logs.append(LogCall(location, function, args))

    def print_funcs(self):
      print(list(map(lambda x: x.get_name(), self.logs)))

    def print(self):
      print(list(map(lambda x: x.print(), self.logs)))

    def find_unique(self):
      self.calls = {}
      for log in self.logs:
        key = log.get_name()
        if key in self.calls:
          self.calls[key] += 1
        else:
          self.calls[key] = 1

    def find_uncalled(self, functions):
      uncalled = []
      for func in functions:
        if func not in self.calls:
          uncalled.append(func)
      return uncalled
        


  def __init__(self):
    # If the singleton hasn't been constructed
    if not LoggerSingleton.instance:
      # Make a new singleton. instance is static so only 1 exists
      LoggerSingleton.instance = LoggerSingleton.__Logger()

  # Allow the singleton to be accessed as if it was __Logger
  def __getattr__(self, name):
    # Return the attribute of the encapsulated class
    return getattr(self.instance, name)

class LogCall:
  # Object to store the object, its method and what arguments its invoked with
  def __init__(self, location, function, *args):
    self.location = location
    self.function = function
    self.args = args

  def get_name(self):
    return "{} => {}".format(self.location, self.function)

  def print(self):
    return "{} : [{}]".format(self.function, self.args)


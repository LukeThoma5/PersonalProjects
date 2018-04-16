from Logger import LoggerSingleton
import inspect

class LoggableObject(object):
  def __init__(self):
    # Get an instance to the logger singleton
    self.logger = LoggerSingleton()
  
  def __getattribute__(self, name):
    # Get the attribute (eg function) by calling the underlying objects
    # getattribute method
    attr = object.__getattribute__(self, name)
    # If we've gotten a method/function, log it
    if inspect.ismethod(attr):
      self.logger.log(name, type(self).__name__)
    return attr
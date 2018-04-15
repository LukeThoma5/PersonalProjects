from Logger import LoggerSingleton
import inspect

class LoggableObject(object):
  def __init__(self):
    self.logger = LoggerSingleton()
  
  def __getattribute__(self, name):
    attr = object.__getattribute__(self, name)
    if inspect.ismethod(attr):
      self.logger.log(name, type(self).__name__)
    return attr
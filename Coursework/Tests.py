from ConversionResult import ConversionResult
from Node import Node
from Graph import Graph, generateDemoGraph
from ExchangeRate import ExchangeRate
import random
import pickle

def extractName(item):
  if hasattr(item, "__name__"):
    return item.__name__
  return str(item)

class TestSuite:
  def __init__(self, name):
    self.tests = []
    self.name = name

  def run(self, shouldPrint=True):
    self.failed = 0
    output = lambda *args: shouldPrint and print(*args)
    output("-"*50)
    output("Running {} tests".format(self.name))
    for test in self.tests:
      try:
        result = test()
        if result:
          pResult = "Passed"
        else:
          pResult = "Failed"
      except:
        result = False
        pResult = "Threw"
      output("{} : {}".format(pResult, test.__name__))
      if not result:
        self.failed += 1
    output("{} total tests: {} failed: {}".format(self.name, len(self.tests), self.failed))

  def getDummySubject(self):
    raise NotImplementedError()

  def case(self, function, *arg):
    lam = lambda: function(*arg)
    lam.__name__ = "{} : [{}]".format(function.__name__, ", ".join(map(lambda x: extractName(x), arg)))
    return lam

class TestSuiteTests(TestSuite):
  def __init__(self):
    super().__init__(type(self).__name__)
    self.tests = [
      self.no_dummy_subject_throws,
      self.cases_work
    ]
    self.run()

  def no_dummy_subject_throws(self):
    subject = TestSuite("DummySubjectSuite")
    subject.tests = [
      self.getDummySubject
    ]
    subject.run(False)
    return subject.failed == 1 and len(subject.tests) == 1

  def cases_work(self):
    def dummy_test_subject(returnValue):
      return returnValue
    subject = TestSuite("CaseTestSuite")
    subject.tests = [
      self.case(dummy_test_subject, True),
      self.case(dummy_test_subject, False)
    ]
    subject.run(False)
    return subject.failed == 1 and len(subject.tests) == 2


class ConversionResultTests(TestSuite):
  def __init__(self):
    super().__init__(type(self).__name__)
    self.tests = [
      self.value_updates_correctly,
      self.getRateFormatted_test,
      self.full_test,
      self.test_chaining
    ]
    self.run()
    
  def getDummySubject(self):
    return ConversionResult(3.14159, [Node("from"), Node("to")])

  def value_updates_correctly(self):
    subject = self.getDummySubject()
    if subject.value != 0:
      return False
    subject.updateValue(10.0)
    return subject.value == 31.4159

  def getRateFormatted_test(self):
    subject = self.getDummySubject()
    twoDp = subject.getRateFormatted()
    threeDp = subject.getRateFormatted(3)
    return twoDp == 3.14 and threeDp == 3.142

  def full_test(self):
    '''Calls repr, getpath, str and get rate formatted'''
    subject = self.getDummySubject()
    return subject.__repr__() == "<Path: from => to, Rate: 3.142, Success: True>"

  def test_chaining(self):
    subject = self.getDummySubject().updateValue(3.0).updateValue(5.0)
    return subject.value == 15.70795


class GraphTests(TestSuite):
  def __init__(self):
    super().__init__(type(self).__name__)
    buying_selector = lambda x: x.buying
    selling_selector = lambda x: x.selling
    buying_selector.__name__ = "buying_selector"
    selling_selector.__name__ = "selling_selector"
    self.tests = [
      # self.demo_graph_made_successfully,
      # self.get_all_currencies_tests,
      # self.case(self.node_exists, "USD", True),
      # self.case(self.node_exists, "Non Existent", False),
      # self.case(self.get_node_expected, "USD", "USD"), #Gets right node
      # self.case(self.get_node_expected, "NONE EXISTENT", "DUMMY"), # Returns dummy node as none found
      # self.save_load_correctly,
      # self.case(self.add_node_correctly, "NEW", 6), # New is added
      # self.case(self.add_node_correctly, "USD", 5), # Existing is ignored
      # self.case(self.add_link_valid_nodes, "USD", "TEST", 4),
      # self.case(self.add_link_valid_nodes, "USD", "NONE EXISTENT", 3),
      # self.case(self.get_exchange_rate_selector, "TEST", "YEN", buying_selector, 2),
      # self.case(self.get_exchange_rate_selector, "YEN", "TEST", buying_selector, 0.5),
      # self.case(self.get_exchange_rate_selector, "TEST", "YEN", selling_selector, 1),
      # self.case(self.get_exchange_rate_selector, "YEN", "TEST", selling_selector, 0.6),
      # self.case(self.get_exchange_rate_selector, "USD", "TEST", buying_selector, -1), # Non exitent direct link
      # self.case(self.get_exchange_rate_selector, "USD", "TEST", selling_selector, -1), # Non exitent direct link
      # # Direct route
      # self.case(self.get_exchange_rate_selector, "GBP", "TEST", buying_selector, 0.2),
      # # Indirect route
      # self.case(self.get_exchange_rate_best, "GBP", "TEST", buying_selector, 1.344),
      # Same for selling route
      self.case(self.get_exchange_rate_selector, "GBP", "TEST", selling_selector, 0.15),
      self.case(self.get_exchange_rate_best, "GBP", "TEST", selling_selector, 1.3104),
    ]
    self.run()    

  def getDummySubject(self):
    return generateDemoGraph()

  def demo_graph_made_successfully(self):
    subject = self.getDummySubject()
    return len(subject.allNodes.keys()) == 5

  def get_all_currencies_tests(self):
    subject = self.getDummySubject()
    return len(subject.allNodes.keys()) == 5 and len(subject.allNodes.keys()) == len(subject.getAllCurrencies())

  def node_exists(self, node, expected):
    subject = self.getDummySubject()
    return subject.nodeExists(node) == expected

  def get_node_expected(self, name, expectedName):
    subject = self.getDummySubject()
    return subject.getNode(name).name == expectedName

  def save_load_correctly(self):
    location = "tests.bin"
    subject = self.getDummySubject()
    subject.tag = random.randint(0, 100)
    subject.save(location)
    loaded = pickle.load(open(location, 'rb'))
    return loaded.tag == subject.tag

  def add_node_correctly(self, nodeName, nodeAmount):
    subject = self.getDummySubject()
    subject.addNode(nodeName)
    return len(subject.allNodes.keys()) == nodeAmount

  def add_link_valid_nodes(self, nameA, nameB, nameALinkCount):
    subject = self.getDummySubject()
    subject.addLink(nameA, nameB, ExchangeRate(1.2))
    return len(subject.getNode(nameA).nodes) == nameALinkCount

  def get_exchange_rate_selector(self, nameA, nameB, selector, value):
     subject = self.getDummySubject()
     rate = subject.getExchangeRate(nameA, nameB, selector)
     print(rate)
     return  rate == value

  def get_exchange_rate_best(self, nameA, nameB, selector, value):
    subject = self.getDummySubject()
    rate = subject.getExchangeRateBest(nameA, nameB, selector)
    print(rate.rate, value, rate.rate == value)
    if not rate.successful:
      return False
    return rate.rate == value
  
def run_tests():
  ConversionResultTests()
  GraphTests()
  TestSuiteTests()

if __name__ == "__main__":
  run_tests()
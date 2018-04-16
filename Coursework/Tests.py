from ConversionResult import ConversionResult
from Node import Node
from NodeLink import NodeLink, buying_selector, selling_selector
from Graph import Graph, generateDemoGraph, matrixBest, matrixDirect
from ExchangeRate import ExchangeRate
from decimal import *
from Logger import LoggerSingleton
import inspect
import random
import pickle
import csv
import sys

SKIP_USER_INPUT_TESTS = True # Ran on load, only do graph ones if asked

def extractName(item):
  if hasattr(item, "__name__"):
    return item.__name__
  return str(item)

def isClose(a, b):
    c = round(Decimal(a), 6)
    d = round(Decimal(b), 6)
    return c == d

class TestSuite:
  def __init__(self, name):
    self.tests = []
    self.name = name

  def run(self, shouldPrint=True):
    self.failed = 0
    self.skipped = 0
    # Define a function so that printing can be disabled
    # A lambda that passes all its arguments to the print function
    # Print function is only executed if shouldPrint is true
    output = lambda *args: shouldPrint and print(*args)
    output("-"*50)
    output("Running {} tests".format(self.name))
    for test in self.tests:
      # A test that throws is a special failing test
      try:
        result = test()
        if result is None:
          pResult = "Skipped"
          self.skipped += 1
        elif result:
          pResult = "Passed"
        else:
          pResult = "Failed"
      except Exception as e:
        print(e)
        result = False
        pResult = "Threw"
        
      # Print the tests name and result
      output("{} : {}".format(pResult, test.__name__))
      if result == False: # If it failed. Explicit to not capture None
        self.failed += 1 # Increase failure count
    output("{} total tests: {} failed: {}".format(self.name, len(self.tests), self.failed))

  def getDummySubject(self):
    raise NotImplementedError()

  def case(self, function, *arg):
    # create a lamda that calls the passed in function with the passed in arguments
    # Done so I can get at the arguments in order to put them in the test name
    lam = lambda: function(*arg)
    lam.__name__ = "{} : [{}]".format(function.__name__, ", ".join(map(lambda x: extractName(x), arg)))
    return lam

class TestSuiteTests(TestSuite):
  def __init__(self):
    super().__init__(type(self).__name__)
    self.tests = [
      self.no_dummy_subject_throws,
      self.cases_work,
      self.only_a_single_logger_exists
    ]

  def no_dummy_subject_throws(self):
    # Test with no defined get dummy subject
    subject = TestSuite("DummySubjectSuite")
    subject.tests = [
      self.getDummySubject
    ]
    # Run without printing enabled
    subject.run(False)
    # Ensure the test failed
    return subject.failed == 1 and len(subject.tests) == 1

  def cases_work(self):
    # Create a dummy test
    def dummy_test_subject(returnValue):
      return returnValue
    subject = TestSuite("CaseTestSuite")
    # Create two tests, one that should fail by returning false
    subject.tests = [
      self.case(dummy_test_subject, True),
      self.case(dummy_test_subject, False)
    ]
    subject.run(False)
    # Check only one of them failed
    return subject.failed == 1 and len(subject.tests) == 2

  def only_a_single_logger_exists(self):
    logger1 = LoggerSingleton()
    logger2 = LoggerSingleton()
    # The is word only matches if they have the same memory address
    # eg same object
    return logger1.logs is logger2.logs


class ConversionResultTests(TestSuite):
  def __init__(self):
    super().__init__(type(self).__name__)
    self.tests = [
      self.value_updates_correctly,
      self.getRateFormatted_test,
      self.full_test,
      self.test_chaining,
      self.case(self.get_result_formatted_test, 2, "6.28"),
      self.case(self.get_result_formatted_test, 3, "6.283"),
    ]
    
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

  def get_result_formatted_test(self, places, result):
    subject = self.getDummySubject()
    subject.updateValue(2)
    return subject.getResultFormatted(places) == result

  def full_test(self):
    '''Calls repr, getpath, str and get rate formatted'''
    subject = self.getDummySubject()
    return subject.__repr__() == "<Path: from => to, Rate: 3.142, Success: True>"

  def test_chaining(self):
    subject = self.getDummySubject().updateValue(3.0).updateValue(5.0)
    return subject.value == 15.70795


class NodeTests(TestSuite):
  def __init__(self):
    super().__init__(type(self).__name__)
    self.tests = [
      self.add_link_adds_link,
      self.case(self.has_link_test, "B", True),
      self.case(self.has_link_test, "None Existent", False),
      self.case(self.update_link_test, "B", 2),
      self.case(self.update_link_test, "None Existent", -1),
    ]

  def getDummySubject(self):
    A = Node("A")
    B = Node("B")
    NodeLink(A, B, ExchangeRate(1))
    return A
    
  def add_link_adds_link(self):
    subject = self.getDummySubject()
    return len(subject.nodes) == 1

  def has_link_test(self, name, expected):
    subject = self.getDummySubject()
    return subject.hasLink(name) == expected

  def update_link_test(self, nodeName, value):
    subject = self.getDummySubject()
    subject.updateLink(nodeName, ExchangeRate(2))
    return subject.getExchangeRate(nodeName, buying_selector) == value

class NodeLinkTests(TestSuite):
  def __init__(self):
    super().__init__(type(self).__name__)
    ordered_compare = lambda x: x.A2B == 3 and x.B2A == 10
    ordered_compare.__name__ = "ordered_compare"
    out_of_order_compare = lambda x: x.B2A == 3 and x.A2B == 10
    out_of_order_compare.__name__ = "out_of_order_compare"
    self.tests = [
      self.get_connecting_node_test,
      self._copy_to_selling_test,
      self.case(self.contains_node_test, "A", True),
      self.case(self.contains_node_test, "B", True),
      self.case(self.contains_node_test, "Nope", False),
      self.case(self.exchange_rate_test, "A", buying_selector, 1),
      self.case(self.exchange_rate_test, "A", selling_selector, 2),
      self.case(self.exchange_rate_test, "B", buying_selector, 1),
      self.case(self.exchange_rate_test, "B", selling_selector, 0.5),
      self.case(self.update_link_test, "A", "B", ordered_compare, buying_selector),
      self.case(self.update_link_test, "B", "A", out_of_order_compare, buying_selector),
      self.case(self.update_link_test, "A", "B", ordered_compare, selling_selector),
      self.case(self.update_link_test, "B", "A", out_of_order_compare, selling_selector),
      self.case(self.print_test, buying_selector, "A => B : 1"),
      self.case(self.print_test, selling_selector, "A => B : 2")      
    ]

  def getDummySubject(self):
    self.A = Node("A")
    self.B = Node("B")
    return NodeLink(self.A, self.B, ExchangeRate(1), ExchangeRate(2))
  
  def get_connecting_node_test(self):
    subject = self.getDummySubject()
    return subject.getConnectingNode(self.A) is self.B and subject.getConnectingNode(self.B) is self.A
    
  def _copy_to_selling_test(self):
    subject = self.getDummySubject()
    subject._copyToSelling()
    return subject.selling.A2B == subject.buying.A2B and subject.selling.B2A == subject.buying.B2A

  def contains_node_test(self, name, value):
    subject = self.getDummySubject()
    return subject.containsNode(name) == value

  def exchange_rate_test(self, name, selector, value):
    subject = self.getDummySubject()
    if name == "A":
      current = self.A
    else:
      current = self.B
    return isClose(subject.getExchangeRate(current, selector), value)

  def update_link_test(self, A, B, comparer, selector):
    subject = self.getDummySubject()
    subject.updateLink(A, B, ExchangeRate(3, 10))
    rate = selector(subject)
    return comparer(rate)

  def print_test(self, selector, result):
    subject = self.getDummySubject()
    return subject.print(selector) == result

class ExchangeRateTests(TestSuite):
  def __init__(self):
    super().__init__(type(self).__name__)
    self.tests = [
      self.sets_fields_correctly,
      self.defaults_fields
    ]

  def sets_fields_correctly(self):
    subject = ExchangeRate(1.5, 1/3)
    return subject.A2B == Decimal(1.5) and subject.B2A == Decimal(1/3)

  def defaults_fields(self):
    subject = ExchangeRate(2)
    return subject.A2B == Decimal(2) and subject.B2A == Decimal(0.5)

class GraphTests(TestSuite):
  def __init__(self):
    super().__init__(type(self).__name__)
    self.tests = [
      self.demo_graph_made_successfully,
      self.get_all_currencies_tests,
      self.case(self.node_exists, "USD", True),
      self.case(self.node_exists, "Non Existent", False),
      self.case(self.get_node_expected, "USD", "USD"), #Gets right node
      self.case(self.get_node_expected, "NONE EXISTENT", "DUMMY"), # Returns dummy node as none found
      self.save_load_correctly,
      self.case(self.add_node_correctly, "NEW", 6), # New is added
      self.case(self.add_node_correctly, "USD", 5), # Existing is ignored
      self.case(self.add_link_valid_nodes, "USD", "TEST", 4),
      self.case(self.add_link_valid_nodes, "USD", "NONE EXISTENT", 3),
      self.case(self.get_exchange_rate_selector, "TEST", "YEN", buying_selector, 2),
      self.case(self.get_exchange_rate_selector, "YEN", "TEST", buying_selector, 0.5),
      self.case(self.get_exchange_rate_selector, "TEST", "YEN", selling_selector, 1),
      self.case(self.get_exchange_rate_selector, "YEN", "TEST", selling_selector, 0.6),
      self.case(self.get_exchange_rate_selector, "USD", "TEST", buying_selector, -1), # Non exitent direct link
      self.case(self.get_exchange_rate_selector, "USD", "TEST", selling_selector, -1), # Non exitent direct link
      # Direct route
      self.case(self.get_exchange_rate_selector, "GBP", "TEST", buying_selector, 0.2),
      # Indirect route
      self.case(self.get_exchange_rate_best, "GBP", "TEST", buying_selector, 1.344),
      # Same for selling route
      self.case(self.get_exchange_rate_selector, "GBP", "TEST", selling_selector, 0.15),
      self.case(self.get_exchange_rate_best, "GBP", "TEST", selling_selector, 1.3104),
      self.case(self.get_all_rates_gets_every_rate, buying_selector),
      self.case(self.get_all_rates_gets_every_rate, selling_selector),
      self.case(self.get_all_rates_gets_every_rate_even_with_unconnected, buying_selector),
      self.case(self.get_all_rates_gets_every_rate_even_with_unconnected, selling_selector),
      self.case(self.updated_rate_is_used, buying_selector, 3.5, True),
      self.case(self.updated_rate_is_used, selling_selector, 2.5, False),
      self.case(self.calc_matrix_is_as_expected, matrixDirect, buying_selector, self.matrix_direct_buying),
      self.case(self.calc_matrix_is_as_expected, matrixDirect, selling_selector, self.matrix_direct_selling),
      self.case(self.calc_matrix_is_as_expected, matrixBest, buying_selector, self.matrix_best_buying),
      self.case(self.calc_matrix_is_as_expected, matrixBest, selling_selector, self.matrix_best_selling),
      self.case(self.buy_vs_sell_graph_test, "USD", matrixBest, 4),
      self.case(self.buy_vs_sell_graph_test, "USD", matrixDirect, 3),
      self.case(self.export_rates_tests, True, "tests-best-buying.csv", buying_selector, self.matrix_best_buying),
      self.get_graph_data_test,
      self.plot_graph_test,
      self.plot_buy_vs_sell_test
    ] 

  def getDummySubject(self):
    return generateDemoGraph()

  def export_rates_tests(self, best, path, selector, matrix):
    subject = self.getDummySubject()
    subject.exportRates(best, path, selector)
    with open(path, 'r', newline='') as csvfile:
      reader = csv.reader(csvfile, quoting=csv.QUOTE_MINIMAL)
      reader.__next__() # Skip over header row
      for index, row in enumerate(reader):
        for index2, item in enumerate(row[1:]):
          if not isClose(matrix[index][index2], item):
            return False
    return True


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
     return  isClose(rate, value)

  def get_exchange_rate_best(self, nameA, nameB, selector, value):
    subject = self.getDummySubject()
    rate = subject.getExchangeRateBest(nameA, nameB, selector)
    if not rate.successful:
      return False
    return isClose(rate.rate, value)

  def get_all_rates_gets_every_rate(self, selector):
    subject = self.getDummySubject()
    GBP = subject.getNode("GBP")
    USD = subject.getNode("USD")
    rates = subject.getAllRates(USD, GBP, [], selector)
    return len(rates) == 3

  def get_all_rates_gets_every_rate_even_with_unconnected(self, selector):
    subject = self.getDummySubject()
    subject.addNode("OTHER")
    GBP = subject.getNode("GBP")
    USD = subject.getNode("USD")
    rates = subject.getAllRates(USD, GBP, [], selector)
    return len(rates) == 3

  def updated_rate_is_used(self, selector, newValue, buying):
    subject = self.getDummySubject()
    original = subject.getExchangeRate("GBP", "TEST", selector)
    buyingRate = ExchangeRate(10, 10)
    sellingRate = ExchangeRate(10, 10)
    if buying:
      buyingRate = ExchangeRate(newValue, newValue)
    else:
      sellingRate = ExchangeRate(newValue, newValue)
    subject.addLink("GBP", "TEST", buyingRate, sellingRate)
    newRate = subject.getExchangeRate("GBP", "TEST", selector)
    return isClose(newRate, newValue) and original != newRate

  def calc_matrix_is_as_expected(self, delegate, selector, result):
    subject = self.getDummySubject()
    matrix = subject.calcRouteMatrix(delegate, selector)
    for index, row in enumerate(matrix):
      for index2, item in enumerate(row):
        if not isClose(result[index][index2], item):
          return False
    return True

  def get_graph_data_test(self):
    subject = self.getDummySubject()
    plots, _ = subject.getGraphData("USD", lambda x: x.buying)
    for index, row in enumerate(plots):
      for index2, item in enumerate(row):
        if not isClose(self.USD_GRAPH_DATA[index][index2], item):
          return False
    return True

  def plot_graph_test(self):
    subject = self.getDummySubject()
    if SKIP_USER_INPUT_TESTS:
      subject.plotGraph
      return None
    subject.plotGraph("USD", lambda x: x.buying)
    return True # If not thrown, pass

  def plot_buy_vs_sell_test(self):
    subject = self.getDummySubject()
    if SKIP_USER_INPUT_TESTS:
      subject.plotBuyVsSell
      return None
    subject.plotBuyVsSell("USD", matrixBest, "Best TEST")
    return True

  USD_GRAPH_DATA = [[1.2, 0.42, 0.35], [1.5, 0.168, 0.05], [0.84, 0.3, 0.25], [1.68, 0.6, 0.5]]
  matrix_direct_buying = [[-1.0, -1.0, -1.0, 0.833333, 1.4], [-1.0, -1.0, 0.2, 1.6, -1.0], [-1.0, 0.2, -1.0, -1.0, 2.0], [1.2, 1.5, -1.0, -1.0, 0.5], [0.7, -1.0, 0.5, 1.25, -1.0]]
  matrix_direct_selling = [[-1.0, -1.0, -1.0, 0.833333, 1.3], [-1.0, -1.0, 0.15, 1.4, -1.0], [-1.0, 0.15, -1.0, -1.0, 1.0], [1.2, 0.8, -1.0, -1.0, 0.5], [0.9, -1.0, 0.6, 1.25, -1.0]]
  matrix_best_buying = [[-1.0, 2.625, 0.7, 1.75, 1.4], [1.92, -1.0, 1.344, 1.6, 2.688], [3.0, 3.75, -1.0, 2.5, 2.0], [1.2, 1.5, 0.84, -1.0, 1.68], [1.5, 1.875, 0.5, 1.25, -1.0]]
  matrix_best_selling = [[-1.0, 1.3, 0.78, 1.625, 1.3], [1.68, -1.0, 1.3104, 1.4, 2.184], [1.5, 1.0, -1.0, 1.25, 1.0], [1.2, 0.8, 0.936, -1.0, 1.56], [1.5, 1.0, 0.6, 1.25, -1.0]]

  def buy_vs_sell_graph_test(self, currency, delegate, expectedLength):
    subject = self.getDummySubject()
    buying, selling, currencies = subject.generateBuySellData(currency, delegate)
    length = len(buying)
    if (length != len(selling) or length != len(currencies)):
      return False
    return length == expectedLength

def get_methods(obj):
  return list(
    filter(lambda x: '__' not in x,
      map(lambda x: "{} => {}".format(type(obj).__name__, x[0]),
      inspect.getmembers(obj,
      predicate=inspect.ismethod))))


def test_completeness():
  Objects = [
    ConversionResult(1),
    Graph(),
    Node(),
    ExchangeRate(1),
    NodeLink(Node("A"), Node("B"), ExchangeRate(1)),
  ]
  logger = LoggerSingleton()
  logger.find_unique()
  functions = []
  for obj in Objects:
    functions.extend(get_methods(obj))
  uncalled = logger.find_uncalled(functions)
  allCalls = list(logger.calls.items())
  allCalls.sort(key=lambda x: x[1], reverse=True)
  print("Most common function calls:")
  for call in zip(allCalls, range(0,10)):
    print("{} calls to {}".format(call[0][1], call[0][0]))
  if len(uncalled) > 0:
    print("The following functions are untested!:")
    for uncalledFunc in uncalled:
      print("WARN:", uncalledFunc)
  else:
    print("All existing functions tested by unit tests")
  

def run_tests():
  testSuites = [
    ConversionResultTests(),
    GraphTests(),
    TestSuiteTests(),
    NodeTests(),
    ExchangeRateTests(),
    NodeLinkTests()
  ]
  total = 0
  failed = 0
  skipped = 0
  for tests in testSuites:
    tests.run()
    total += len(tests.tests)
    failed += tests.failed
    skipped += tests.skipped
  print("-"*50)
  print("Completed {} tests with {} failures {} skips".format(total, failed, skipped))
  print("To enable full testing run with noskip flag enabled. '$ py Tests.py noskip'")
  test_completeness()
  return (total, failed, skipped)


if __name__ == "__main__":
  SKIP_USER_INPUT_TESTS = len(sys.argv) == 1
  run_tests()
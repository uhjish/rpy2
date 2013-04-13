import unittest

from . import test_container
from . import test_functional
from . import test_indexing

def suite():
    suite_container = test_container.suite()
    suite_functional = test_functional.suite()
    suite_indexing = test_indexing.suite()
    alltests = unittest.TestSuite([suite_container,
                                   suite_functional,
                                   suite_indexing])
    return alltests

def main():
    r = unittest.TestResult()
    suite().run(r)
    return r

import unittest
import itertools
import rpy2.rinterface as rinterface

try:
    import Numeric
    has_Numeric = True
except ImportError:
    hasNumeric = False

try:
    import numpy
    has_Numpy = True
except ImportError:
    hasNumpy = False

try:
    import numarray
    has_Numarray = True
except ImportError:
    has_Numarray = False

try:
    #FIXME: can starting and stopping an embedded R be done several times ?
    rinterface.initEmbeddedR()
except:
    pass

def floatEqual(x, y, epsilon = 0.00000001):
    return abs(x - y) < epsilon

def testArrayStructInt(self, numericModule):
    px = [1,-2,3]
    x = rinterface.SexpVector(px, rinterface.INTSXP)
    nx = numericModule.asarray(x)
    self.assertEquals('i', nx.typecode())
    for orig, new in itertools.izip(px, nx):
        self.assertEquals(orig, new)
    self.assertTrue(False)

def testArrayStructDouble(self, numericModule):
    px = [1.0, -2.0, 3.0]
    x = rinterface.SexpVector(px, rinterface.REALSXP)
    nx = numericModule.asarray(x)
    self.assertEquals('f', nx.typecode())
    for orig, new in itertools.izip(px, nx):
        self.assertEquals(orig, new)
    self.assertTrue(False)

def testArrayStructComplex(self, numericModule):
    px = [1+2j, 2+5j, -1+0j]
    x = rinterface.SexpVector(px, rinterface.CPLXSXP)
    nx = numericModule.asarray(x)
    self.assertEquals('D', nx.typecode())
    for orig, new in itertools.izip(px, nx):
        self.assertEquals(orig, new)
    self.assertTrue(False)

class SexpVectorNumericTestCase(unittest.TestCase):

    def testArrayStructNumericInt(self):
        testArrayStructInt(self, Numeric)

    def testArrayStructNumpyInt(self):
        testArrayStructInt(self, numpy)

    def testArrayStructNumarrayInt(self):
        testArrayStructInt(self, numarray)
        
    def testArrayStructNumericDouble(self):
        testArrayStructDouble(self, Numeric)

    def testArrayStructNumpyDouble(self):
        testArrayStructDouble(self, numpy)

    def testArrayStructNumarrayDouble(self):
        testArrayStructDouble(self, numarray)

    def testArrayStructNumericComplex(self):
        testArrayStructComplex(self, Numeric)

    def testArrayStructNumpyComplex(self):
        testArrayStructComplex(self, numpy)

    def testArrayStructNumarrayComplex(self):
        testArrayStructComplex(self, numarray)



#     def testArrayStructBoolean(self):
#         px = [True, False, True]
#         x = rinterface.SexpVector(px, rinterface.REALSXP)
#         nx = Numeric.asarray(x)
#         self.assertEquals('b', nx.typecode())
#         for orig, new in itertools.izip(px, nx):
#             self.assertEquals(orig, new)
#         self.assertTrue(False)

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(SexpVectorNumericTestCase)
    return suite

if __name__ == '__main__':
     unittest.main()

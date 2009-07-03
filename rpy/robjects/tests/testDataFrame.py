import unittest
import rpy2.robjects as robjects
rinterface = robjects.rinterface
import rpy2.rlike.container as rlc

import array

class DataFrameTestCase(unittest.TestCase):

    def testNewFromTaggedList(self):
        letters = robjects.r.letters        
        numbers = robjects.r('1:26')
        df = robjects.DataFrame(rlc.TaggedList((letters, numbers),
                                               tags = ('letters', 'numbers')))

        self.assertEquals("data.frame", df.rclass[0])

    def testNewFromRObject(self):
        numbers = robjects.r('1:5')
        self.assertRaises(ValueError, robjects.DataFrame, numbers)

        rlist = robjects.r('list(a=1, b=2, c=3)')
        self.assertRaises(ValueError, robjects.DataFrame, rlist)

        rdataf = robjects.r('data.frame(a=1:2, b=c("a", "b"))')
        dataf = robjects.DataFrame(rdataf)        

    def testNewFromOrdDict(self):
        od = rlc.OrdDict(c=(('a', robjects.IntVector((1,2))),
                            ('b', robjects.StrVector(('c', 'd')))
                            ))
        dataf = robjects.DataFrame(od)
        self.assertEquals(1, dataf.rx2('a')[0])
        
    def testDim(self):
        letters = robjects.r.letters        
        numbers = robjects.r('1:26')
        df = robjects.DataFrame(rlc.TaggedList((letters, numbers),
                                               tags = ('letters', 'numbers')))
        self.assertEquals(26, df.nrow)
        self.assertEquals(2, df.ncol)

    def testFrom_csvfile(self):
        self.assertTrue(False) # no test yet

    def testTo_csvfile(self):
        self.assertTrue(False) # no test yet

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(DataFrameTestCase)
    return suite

if __name__ == '__main__':
     unittest.main()

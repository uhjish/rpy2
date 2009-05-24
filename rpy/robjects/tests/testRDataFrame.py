import unittest
import rpy2.robjects as robjects
rinterface = robjects.rinterface
import rpy2.rlike.container as rlc

import array

class RDataFrameTestCase(unittest.TestCase):

    def testNewFromTaggedList(self):
        letters = robjects.r.letters        
        numbers = robjects.r('1:26')
        df = robjects.RDataFrame(rlc.TaggedList((letters, numbers),
                                                tags = ('letters', 'numbers')))

        self.assertEquals("data.frame", df.rclass[0])

    def testNewFromRObject(self):
        numbers = robjects.r('1:5')
        self.assertRaises(ValueError, robjects.RDataFrame, numbers)

        rlist = robjects.r('list(a=1, b=2, c=3)')
        self.assertRaises(ValueError, robjects.RDataFrame, rlist)

        rdataf = robjects.r('data.frame(a=1:2, b=c("a", "b"))')
        dataf = robjects.RDataFrame(rdataf)        

    def testNewFromDict(self):
        d = {'a': robjects.IntVector((1,2)),
             'b': robjects.StrVector(('c', 'd'))}
        dataf = robjects.RDataFrame(**d)
        self.assertEquals('c', dataf.r['b'][0][0])
        
    def testDim(self):
        letters = robjects.r.letters        
        numbers = robjects.r('1:26')
        df = robjects.RDataFrame(rlc.TaggedList((letters, numbers),
                                                tags = ('letters', 'numbers')))

        self.assertEquals(26, df.nrow())
        self.assertEquals(2, df.ncol())


def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(RDataFrameTestCase)
    return suite

if __name__ == '__main__':
     unittest.main()

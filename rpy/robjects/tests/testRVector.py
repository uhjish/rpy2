import unittest
import rpy2.robjects as robjects
ri = robjects.rinterface
import array

rlist = robjects.baseNameSpaceEnv["list"]

class RVectorTestCase(unittest.TestCase):

    def testNew(self):
        identical = ri.baseNameSpaceEnv["identical"]
        py_a = array.array('i', [1,2,3])
        ro_v = robjects.RVector(py_a)
        self.assertEquals(ro_v.typeof(), ri.INTSXP)
        
        ri_v = ri.SexpVector(py_a, ri.INTSXP)
        ro_v = robjects.RVector(ri_v)

        self.assertTrue(identical(ro_v, ri_v)[0])

        del(ri_v)
        self.assertEquals(ri.INTSXP, ro_v.typeof())
        
    def testOperators(self):
        seq_R = robjects.r["seq"]
        mySeq = seq_R(0, 10)
        mySeqAdd = mySeq + 2
        for i, li in enumerate(mySeq):
            self.assertEquals(i + 2, mySeqAdd[i])

        mySeqAdd = mySeq + mySeq
        for i, li in enumerate(mySeq):
            self.assertEquals(mySeq[i] * 2, mySeqAdd[i])

        
    def testSubset(self):
        seq_R = robjects.baseNameSpaceEnv["seq"]
        mySeq = seq_R(0, 10)
        # R indexing starts at one
        myIndex = robjects.RVector(array.array('i', range(1, 11, 2)))

        mySubset = mySeq.subset(myIndex)
        for i, si in enumerate(myIndex):
            self.assertEquals(mySeq[si-1], mySubset[i])

    def testSubsetRecyclingRule(self):
        # recycling rule
        v = robjects.RVector(array.array('i', range(1, 23)))
        m = robjects.r.matrix(v, ncol = 2)
        col = m.subset(True, 1)
        self.assertEquals(11, len(col))

    def testSubsetLiet(self):
        # list
        letters = robjects.baseNameSpaceEnv["letters"]
        myList = rlist(l=letters, f="foo")
        idem = robjects.baseNameSpaceEnv["identical"]
        self.assertTrue(idem(letters, myList.subset("l")[0]))
        self.assertTrue(idem("foo", myList.subset("f")[0]))

    def testGetItem(self):
        letters = robjects.baseNameSpaceEnv["letters"]
        self.assertEquals('a', letters[0])
        self.assertEquals('z', letters[25])

    def testGetItemOutOfBounds(self):
        letters = robjects.baseNameSpaceEnv["letters"]
        self.assertRaises(IndexError, letters.__getitem__, 26)

    def getItemList(self):
        mylist = rlist(letters, "foo")
        idem = robjects.baseNameSpaceEnv["identical"]
        self.assertTrue(idem(letters, mylist[0]))
        self.assertTrue(idem("foo", mylist[1]))

    def testGetNames(self):
        vec = robjects.RVector(array.array('i', [1,2,3]))
        v_names = [robjects.baseNameSpaceEnv["letters"][x] for x in (0,1,2)]
        #FIXME: simplify this
        r_names = robjects.baseNameSpaceEnv["c"](*v_names)
        vec = robjects.r["names<-"](vec, r_names)
        for i in xrange(len(vec)):
            self.assertEquals(v_names[i], vec.getNames()[i])

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(RVectorTestCase)
    return suite

if __name__ == '__main__':
     unittest.main()

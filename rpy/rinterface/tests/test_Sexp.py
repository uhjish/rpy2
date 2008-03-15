import unittest
import rpy.rinterface as rinterface

#FIXME: can starting and stopping an embedded R be done several times ?
rinterface.initEmbeddedR("foo", "--vanilla", "--no-save", "--quiet")

class SexpTestCase(unittest.TestCase):
    #def setUpt(self):
    #    rinterface.initEmbeddedR("foo", "--no-save")

    #def tearDown(self):
    #    rinterface.endEmbeddedR(1);

    def testTypeof(self):
        sexp = rinterface.globalEnv.get("letters")
        self.assertEquals(sexp.typeof(), rinterface.STRSXP)
        
        sexp = rinterface.globalEnv.get("pi")
        self.assertEquals(sexp.typeof(), rinterface.REALSXP)
        
        sexp = rinterface.globalEnv.get("plot")
        self.assertEquals(sexp.typeof(), rinterface.CLOSXP)

    def testDo_slot(self):
        data_func = rinterface.globalEnv.get("data")
        data_func(rinterface.SexpVector(["iris", ], rinterface.STRSXP))
        sexp = rinterface.globalEnv.get("iris")
        names = sexp.do_slot("names")
        iris_names = ("Sepal.Length", "Sepal.Width", "Petal.Length", "Petal.Width", "Species")

        self.assertEquals(len(iris_names), len(names))

        for i, n in enumerate(iris_names):
            self.assertEquals(iris_names[i], names[i])

        missing = sexp.do_slot("foo")       

if __name__ == '__main__':
     unittest.main()

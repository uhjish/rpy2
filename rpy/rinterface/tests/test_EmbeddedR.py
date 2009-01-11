import unittest
import itertools
import rpy2.rinterface as rinterface
import os, subprocess, time, tempfile, signal

rinterface.initr()

class EmbeddedRTestCase(unittest.TestCase):
    def testSetWriteConsole(self):
        buf = []
        def f(x):
            buf.append(x)

        rinterface.setWriteConsole(f)
        code = rinterface.SexpVector(["3", ], rinterface.STRSXP)
        rinterface.baseNameSpaceEnv["print"](code)
        self.assertEquals('[1] "3"\n', str.join('', buf))
        rinterface.setWriteConsole(rinterface.consolePrint)

    def testSetReadConsole(self):
        yes = "yes\n"
        def sayyes(prompt):
            return(yes)
        rinterface.setReadConsole(sayyes)
        res = rinterface.baseNameSpaceEnv["readline"]()
        self.assertEquals(yes.strip(), res[0])
        rinterface.setReadConsole(rinterface.consoleRead)
        
    def testSetShowMessage(self):
        self.assertTrue(False) # no unit test (yet)

    def testSetChooseFile(self):
        self.assertTrue(False) # no unit test (yet)

#FIXME: end and initialize again causes currently a lot a trouble...
    def testCallErrorWhenEndedR(self):
        self.assertTrue(False) # worked when tested, but calling endEmbeddedR causes trouble
        t = rinterface.baseNameSpaceEnv['date']
        rinterface.endr(1)
        self.assertRaises(RuntimeError, t)
        rinterface.initr()

    def testStr_typeint(self):
        t = rinterface.baseNameSpaceEnv['letters']
        self.assertEquals('STRSXP', rinterface.str_typeint(t.typeof))
        t = rinterface.baseNameSpaceEnv['pi']
        self.assertEquals('REALSXP', rinterface.str_typeint(t.typeof))

    def testStr_typeint_invalid(self):
        self.assertRaises(LookupError, rinterface.str_typeint, 99)

    def testGet_initoptions(self):
        options = rinterface.get_initoptions()
        self.assertEquals(len(rinterface.initoptions),
                          len(options))
        for o1, o2 in itertools.izip(rinterface.initoptions, options):
            self.assertEquals(o1, o2)
        
    def testSet_initoptions(self):
        self.assertRaises(RuntimeError, rinterface.set_initoptions, 
                          ('aa', '--verbose', '--no-save'))

    def testInterruptR(self):
        rpy_code = tempfile.NamedTemporaryFile(mode = 'w', suffix = '.py',
                                               delete = False)
        rpy_code_str = os.linesep.join(['''import rpy2.robjects as ro''',
                                        '''ro.r('i <- 0''',
                                        '''while(TRUE) {''',
                                        '''    i <- i+1''',
                                        '''    Sys.sleep(0.01)''',
                                        '''}') '''])
        rpy_code.write(rpy_code_str)
        rpy_code.close()
        child_proc = subprocess.Popen(('python', rpy_code.name))
        #child_proc = subprocess.Popen(('sleep', '113'))
        #import pdb; pdb.set_trace()
        child_proc.send_signal(signal.SIGINT)
        ret_code = child_proc.poll()
        #print(ret_code)
        #import pdb; pdb.set_trace()
        self.assertFalse(ret_code is None) # Interruption failed

class ObjectDispatchTestCase(unittest.TestCase):
    def testObjectDispatchLang(self):
        formula = rinterface.globalEnv.get('formula')
        obj = formula(rinterface.StrSexpVector(['y ~ x', ]))
        self.assertTrue(isinstance(obj, rinterface.SexpVector))
        self.assertEquals(rinterface.LANGSXP, obj.typeof)

    def testObjectDispatchVector(self):
        letters = rinterface.globalEnv.get('letters')
        self.assertTrue(isinstance(letters, rinterface.SexpVector))

    def testObjectDispatchClosure(self):
        #import pdb; pdb.set_trace()
        help = rinterface.globalEnv.get('sum')
        self.assertTrue(isinstance(help, rinterface.SexpClosure))

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(EmbeddedRTestCase)
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(ObjectDispatchTestCase))
    return suite

if __name__ == '__main__':
     unittest.main()

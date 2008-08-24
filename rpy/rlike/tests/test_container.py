import unittest
import itertools
import rpy2.rlike.container as rlc

class ArgsDictTestCase(unittest.TestCase):

    def testNew(self):
        nl = rlc.ArgsDict()

        x = (('a', 123), ('b', 456), ('c', 789))
        nl = rlc.ArgsDict(x)

    def testLen(self):
        x = rlc.ArgsDict()
        self.assertEquals(0, len(x))

        x['a'] = 2
        x['b'] = 1

        self.assertEquals(2, len(x))

    def testGetSetitem(self):
        x = rlc.ArgsDict()
        
        x['a'] = 1
        self.assertEquals(1, len(x))
        self.assertEquals(1, x['a'])
        self.assertEquals(0, x.index('a'))
        x['a'] = 2
        self.assertEquals(1, len(x))
        self.assertEquals(2, x['a'])
        self.assertEquals(0, x.index('a'))
        x['b'] = 1
        self.assertEquals(2, len(x))
        self.assertEquals(1, x['b'])
        self.assertEquals(1, x.index('b'))
        
    def testGetSetitemWithNone(self):
        x = rlc.ArgsDict()
        
        x['a'] = 1
        x[None] = 2
        self.assertEquals(2, len(x))
        x['b'] = 5
        self.assertEquals(3, len(x))
        self.assertEquals(1, x['a'])
        self.assertEquals(5, x['b'])
        self.assertEquals(0, x.index('a'))
        self.assertEquals(2, x.index('b'))
        
    def testReverse(self):
        x = rlc.ArgsDict()
        x['a'] = 3
        x['b'] = 2
        x['c'] = 1
        x.reverse()
        self.assertEquals(1, x['c'])
        self.assertEquals(0, x.index('c'))
        self.assertEquals(2, x['b'])
        self.assertEquals(1, x.index('b'))
        self.assertEquals(3, x['a'])
        self.assertEquals(2, x.index('a'))

    def testItems(self):

        args = (('a', 5), ('b', 4), ('c', 3),
                ('d', 2), ('e', 1))
        x = rlc.ArgsDict(args)
        it = x.items()
        for ki, ko in itertools.izip(args, it):
            self.assertEquals(ki[0], ko[0])
            self.assertEquals(ki[1], ko[1])

class TaggedListTestCase(unittest.TestCase):

    def test__add__(self):
        tn = ['a', 'b', 'c']
        tv = [1,2, 3]
        tl = rlc.TaggedList(tv, tags = tn)
        tl = tl + tl
        self.assertEquals(6, len(tl))
        self.assertEquals(('a', 'b', 'c', 'a', 'b', 'c'), tl.tags())
        self.assertEquals((1,2,3,1,2,3), tuple(tl))

    def test__delitem__(self):
        tn = ['a', 'b', 'c']
        tv = [1,2,3]
        tl = rlc.TaggedList(tv, tags = tn)
        self.assertEquals(3, len(tl))
        del tl[1]
        self.assertEquals(2, len(tl))
        self.assertEquals(tl.tags(), ('a', 'c'))
        self.assertEquals(tuple(tl), (1, 3))

    def test__delslice__(self):
        tn = ['a', 'b', 'c', 'd']
        tv = [1,2,3,4]
        tl = rlc.TaggedList(tv, tags = tn)
        del tl[1:3]
        self.assertEquals(2, len(tl))
        self.assertEquals(tl.tags(), ('a', 'd'))
        self.assertEquals(tuple(tl), (1, 4))

    def test__iadd__(self):
        tn = ['a', 'b', 'c']
        tv = [1, 2, 3]
        tl = rlc.TaggedList(tv, tags = tn)
        tl += tl
        self.assertEquals(6, len(tl))
        self.assertEquals(('a', 'b', 'c', 'a', 'b', 'c'), tl.tags())
        self.assertEquals((1,2,3,1,2,3), tuple(tl))

    def test__imul__(self):
        tn = ['a', 'b']
        tv = [1,2]
        tl = rlc.TaggedList(tv, tags = tn)
        tl *= 3
        self.assertEquals(6, len(tl))
        self.assertEquals(('a', 'b', 'a', 'b', 'a', 'b'), tl.tags())
        self.assertEquals((1,2,1,2,1,2), tuple(tl))

    def test__init__(self):
        tn = ['a', 'b', 'c']
        tv = [1,2,3]
        tl = rlc.TaggedList(tv, tags = tn)

        self.assertRaises(TypeError, rlc.TaggedList, tv, tags=123)
        self.assertRaises(ValueError, rlc.TaggedList, tv, tags=('a', 'b'))        

    def test__setslice__(self):
        tn = ['a', 'b', 'c', 'd']
        tv = [1,2,3,4]
        tl = rlc.TaggedList(tv, tags = tn)
        tl[1:3] = [5, 6]
        self.assertEquals(4, len(tl))
        self.assertEquals(tl.tags(), ('a', 'b', 'c', 'd'))
        self.assertEquals(tuple(tl), (1, 5, 6, 4))

    def testappend(self):
        tn = ['a', 'b', 'c']
        tv = [1,2,3]
        tl = rlc.TaggedList(tv, tags = tn)
        self.assertEquals(3, len(tl))
        tl.append(4, tag='a')
        self.assertEquals(4, len(tl))
        self.assertEquals(4, tl[3])
        self.assertEquals(('a', 'b', 'c', 'a'), tl.tags())

    def testextend(self):
        tn = ['a', 'b', 'c']
        tv = [1,2,3]
        tl = rlc.TaggedList(tv, tags = tn)
        tl.extend([4, 5])
        self.assertEquals(('a', 'b', 'c', None, None), tuple(tl.itertags()))
        self.assertEquals((1, 2, 3, 4, 5), tuple(tl))

    def testinsert(self):
        tn = ['a', 'b', 'c']
        tv = [1,2,3]
        tl = rlc.TaggedList(tv, tags = tn)
        tl.insert(1, 4, tag = 'd')
        self.assertEquals(('a', 'd', 'b', 'c'), tuple(tl.itertags()))
        self.assertEquals((1, 4, 2, 3), tuple(tl))
        
    def testitems(self):
        tn = ['a', 'b', 'c']
        tv = [1,2,3]
        tl = rlc.TaggedList(tv, tags = tn)
        self.assertEquals((('a', 1), ('b', 2), ('c', 3)), 
                          tl.items())

    def testiterontag(self):
        tn = ['a', 'b', 'a', 'c']
        tv = [1,2,3,4]
        tl = rlc.TaggedList(tv, tags = tn)
        self.assertEquals((1, 3), tuple(tl.iterontag('a')))

    def testitertags(self):
        tn = ['a', 'b', 'c']
        tv = [1,2,3]
        tl = rlc.TaggedList(tv, tags = tn)
        self.assertEquals(('a', 'b', 'c'), tuple(tl.itertags()))

    def testpop(self):
        tn = ['a', 'b', 'c']
        tv = [1,2,3]
        tl = rlc.TaggedList(tv, tags = tn)
        self.assertEquals(3, len(tl))
        tl.pop()
        self.assertEquals(2, len(tl))
        self.assertEquals(tl.tags(), ('a', 'b'))
        self.assertEquals(tuple(tl), (1, 2))

        tl.pop(0)
        self.assertEquals(1, len(tl))
        self.assertEquals(tl.tags(), ('b', ))

    def testremove(self):
        tn = ['a', 'b', 'c']
        tv = [1,2,3]
        tl = rlc.TaggedList(tv, tags = tn)
        self.assertEquals(3, len(tl))
        tl.remove(2)
        self.assertEquals(2, len(tl))
        self.assertEquals(tl.tags(), ('a', 'c'))
        self.assertEquals(tuple(tl), (1, 3))

    def testreverse(self):
        tn = ['a', 'b', 'c']
        tv = [1,2,3]
        tl = rlc.TaggedList(tv, tags = tn)
        tl.reverse()
        self.assertEquals(3, len(tl))
        self.assertEquals(tl.tags(), ('c', 'b', 'a'))
        self.assertEquals(tuple(tl), (3, 2, 1))

    def testsort(self):
        tn = ['a', 'c', 'b']
        tv = [1,3,2]
        tl = rlc.TaggedList(tv, tags = tn)
        tl.sort()

        self.assertEquals(tl.tags(), ('a', 'b', 'c'))
        self.assertEquals(tuple(tl), (1, 2, 3))
        
    def testtags(self):
        tn = ['a', 'b', 'c']
        tv = [1,2,3]
        tl = rlc.TaggedList(tv, tags = tn)
        tags = tl.tags()
        self.assertTrue(isinstance(tags, tuple))
        self.assertEquals(tags, ('a', 'b', 'c'))

    def testsettag(self):
        tn = ['a', 'b', 'c']
        tv = [1,2,3]
        tl = rlc.TaggedList(tv, tags = tn)
        tl.settag(1, 'z')
        self.assertEquals(tl.tags(), ('a', 'z', 'c'))
    
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(ArgsDictTestCase)
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TaggedListTestCase))
    return suite

if __name__ == '__main__':
     unittest.main()

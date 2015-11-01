import os, sys
import tempfile
import weakref
import rpy2.rinterface

rpy2.rinterface.initr()

from . import conversion

class RSlots(object):
    """ Attributes of an R object as a Python mapping.

    The parent proxy to the underlying R object is held as a
    weak reference. The attributes are therefore not protected
    from garbage collection unless bound to a Python symbol or
    in an other container.
    """
    
    __slots__ = ['_robj', ]
    
    def __init__(self, robj):
        self._robj = weakref.proxy(robj)

        
    def __getitem__(self, key):
        value = self._robj.do_slot(key)
        return conversion.ri2ro(value)
        
    def __setitem__(self, key, value):
        rpy2_value = conversion.py2ri(value)
        self._robj.do_slot_assign(key, rpy2_value)

    def __len__(self):
        return len(self._robj.list_attrs())
    
    def keys(self):
        for k in self._robj.list_attrs():
            yield k

    def items(self):
        for k in self._robj.list_attrs():
            v = self[key]
            yield (k, v)

    def values(self):
        for k in self._robj.list_attrs():
            v = self[key]
            yield v

        
class RObjectMixin(object):
    """ Class to provide methods common to all RObject instances """
    __rname__ = None

    __tempfile = rpy2.rinterface.baseenv.get("tempfile")
    __file = rpy2.rinterface.baseenv.get("file")
    __fifo = rpy2.rinterface.baseenv.get("fifo")
    __sink = rpy2.rinterface.baseenv.get("sink")
    __close = rpy2.rinterface.baseenv.get("close")
    __readlines = rpy2.rinterface.baseenv.get("readLines")
    __unlink = rpy2.rinterface.baseenv.get("unlink")
    __rclass = rpy2.rinterface.baseenv.get("class")
    __rclass_set = rpy2.rinterface.baseenv.get("class<-")
    __show = rpy2.rinterface.baseenv.get("show")

    __slots = None
    
    @property
    def slots(self):
        """ Attributes of the underlying R object as a Python mapping.

        The attributes can accessed and assigned by name (as if they
        were in a Python `dict`)."""
        if self.__slots is None:
            self.__slots = RSlots(self)
        return self.__slots

    def __str__(self):
        if sys.platform == 'win32':
            tmpf = tempfile.NamedTemporaryFile(delete=False)
            tfname = tmpf.name
            tmp = self.__file(rpy2.rinterface.StrSexpVector([tfname,]),
                              open=rpy2.rinterface.StrSexpVector(["r+", ]))
            self.__sink(tmp)
        else:
            writeconsole = rpy2.rinterface.get_writeconsole_regular()
            s = []
            def f(x):
                s.append(x)
            rpy2.rinterface.set_writeconsole_regular(f)
        self.__show(self)
        if sys.platform == 'win32':
            self.__sink()
            s = tmpf.readlines()
            tmpf.close()
            self.__close(tmp)
            try:
                del tmpf
                os.unlink(tfname)
            except WindowsError:
                if os.path.exists(tfname):
                    print('Unable to unlink tempfile %s' % tfname)
            s = str.join(os.linesep, s)
        else:
            rpy2.rinterface.set_writeconsole_regular(writeconsole)
            s = str.join('', s)
        return s

    def r_repr(self):
        """ String representation for an object that can be
        directly evaluated as R code.
        """
        return repr_robject(self, linesep='\n')

    def _rclass_get(self):
        try:
            res = self.__rclass(self)
            #res = conversion.ri2py(res)
            return res
        except rpy2.rinterface.RRuntimeError as rre:
            if self.typeof == rpy2.rinterface.SYMSXP:
                #unevaluated expression: has no class
                return (None, )
            else:
                raise rre
    def _rclass_set(self, value):
        res = self.__rclass_set(self, value)
        self.__sexp__ = res.__sexp__
            
    rclass = property(_rclass_get, _rclass_set, None,
                      "R class for the object, stored as an R string vector.")


    
def repr_robject(o, linesep=os.linesep):
    s = rpy2.rinterface.baseenv.get("deparse")(o)
    s = str.join(linesep, s)
    return s

    
class RObject(RObjectMixin, rpy2.rinterface.Sexp):
    """ Base class for all R objects. """
    
    def __setattr__(self, name, value):
        if name == '_sexp':
            if not isinstance(value, rpy2.rinterface.Sexp):
                raise ValueError("_attr must contain an object " +\
                                     "that inherits from rpy2.rinterface.Sexp" +\
                                     "(not from %s)" %type(value))
        super(RObject, self).__setattr__(name, value)


from types import ModuleType
import rpy2.rinterface as rinterface
import rpy2.robjects.lib
import conversion as conversion
from rpy2.robjects.functions import SignatureTranslatedFunction
from rpy2.robjects.constants import NULL

_require = rinterface.baseenv['require']
_as_env = rinterface.baseenv['as.environment']
_package_has_namespace = rinterface.baseenv['packageHasNamespace']
_system_file = rinterface.baseenv['system.file']
_get_namespace = rinterface.baseenv['getNamespace']
_get_namespace_exports = rinterface.baseenv['getNamespaceExports']
_find_package = rinterface.baseenv['.find.package']
_packages = rinterface.baseenv['.packages']
_libpaths = rinterface.baseenv['.libPaths']
_loaded_namespaces = rinterface.baseenv['loadedNamespaces']

def quiet_require(name, lib_loc = None):
    """ Load an R package /quietly/ (suppressing messages to the console). """
    if lib_loc == None:
        lib_loc = "NULL"
    expr_txt = "suppressPackageStartupMessages(base::require(%s, lib.loc=%s))" \
        %(name, lib_loc)
    expr = rinterface.parse(expr_txt)
    ok = rinterface.baseenv['eval'](expr)
    return ok

def get_packagepath(package):
    """ return the path to an R package installed """
    res = _find_package(rinterface.StrSexpVector((package, )))
    return res[0]


class Package(ModuleType):
    """ Models an R package
    (and can do so from an arbitrary environment - with the caution
    that locked environments should mostly be considered).
     """
    
    _env = None
    __rname__ = None
    _translation = None
    _rpy2r = None
    __fill_rpy2r__ = None
    __update_dict__ = None
    _exported_names = None

    def __init__(self, env, name, translation = {}, 
                 exported_names = None):
        """ Create a Python module-like object from an R environment,
        using the specified translation if defined. """
        super(Package, self).__init__(name)
        self._env = env
        self.__rname__ = name
        self._translation = translation
        mynames = tuple(self.__dict__)
        self._rpy2r = {}
        if exported_names is None:
            exported_names = set(self._env.keys())
        self._exported_names = exported_names
        self.__fill_rpy2r__()
        self.__update_dict__()
        self._exported_names = self._exported_names.difference(mynames)
                
    def __update_dict__(self):
        """ Update the __dict__ according to what is in the R environment """
        for elt in self._rpy2r:
            del(self.__dict__[elt])
        self._rpy2r = {}
        self.__fill_rpy2r__()

    def __fill_rpy2r__(self):
        """ Fill the attribute _rpy2r """
        name = self.__rname__
        for rname in self._env:
            if rname in self._translation:
                rpyname = self._translation[rname]
            else:
                dot_i = rname.find('.')
                if dot_i > -1:
                    rpyname = rname.replace('.', '_')
                    if rpyname in self._rpy2r:
                        msg = ('Conflict when converting R symbol'+\
                                   ' to a Python symbol ' +\
                                   '(%s -> %s while there is already'+\
                                   ' %s)') %(rname, rpyname,
                                             rpyname)
                        raise LibraryError(msg)
                else:
                    rpyname = rname
                if rpyname in self.__dict__ or rpyname == '__dict__':
                    raise LibraryError('The symbol ' + rname +\
                                       ' in the package ' + name + \
                                       ' is conflicting with ' +\
                                       'a Python object attribute')
            self._rpy2r[rpyname] = rname
            if (rpyname != rname) and (rname in self._exported_names):
                self._exported_names.remove(rname)
                self._exported_names.add(rpyname)
            rpyobj = conversion.ri2py(self._env[rname])
            if hasattr(rpyobj, '__rname__'):
                rpyobj.__rname__ = rname
            #FIXME: shouldn't the original R name be also in the __dict__ ?
            self.__dict__[rpyname] = rpyobj


    def __repr__(self):
        s = super(Package, self).__repr__()
        return 'rpy2.robjecs.packages.Package as a ' + s

class SignatureTranslatedPackage(Package):
    def __fill_rpy2r__(self):
        super(SignatureTranslatedPackage, self).__fill_rpy2r__()
        for name, robj in self.__dict__.iteritems():
            if isinstance(robj, rinterface.Sexp) and robj.typeof == rinterface.CLOSXP:
                self.__dict__[name] = SignatureTranslatedFunction(self.__dict__[name])
                

class LibraryError(ImportError):
    """ Error occuring when importing an R library """
    pass



def importr(name, 
            lib_loc = None,
            robject_translations = {}, signature_translation = True,
            suppress_messages = True):
    """ Import an R package.

    Arguments:

    - name: name of the R package

    - lib_loc: specific location for the R library (default: None)

    - robject_translations: dict (default: {})

    - signature_translation: dict (default: {})

    - suppress_message: Suppress messages R usually writes on the console
      (defaut: True)

    Return:

    - an instance of class SignatureTranslatedPackage, or of class Package 

    """

    rname = rinterface.StrSexpVector((name, ))

    if suppress_messages:
        ok = quiet_require(name, lib_loc = lib_loc)
    else:
        ok = _require(rinterface.StrSexpVector(rname), **{'lib.loc': lib_loc})[0]
    if not ok:
        raise LibraryError("The R package %s could not be imported" %name)
    if _package_has_namespace(rname, 
                              _system_file(package = rname)):
        env = _get_namespace(rname)
        exported_names = set(_get_namespace_exports(rname))
    else:
        env = _as_env(rinterface.StrSexpVector(['package:'+name, ]))
        exported_names = None

    if signature_translation:
        pack = SignatureTranslatedPackage(env, name, 
                                          translation = robject_translations,
                                          exported_names = exported_names)
    else:
        pack = Package(env, name, translation = robject_translations,
                       exported_names = exported_names)
        
    return pack


def wherefrom(symbol, startenv = rinterface.globalenv):
    """ For a given symbol, return the environment
    this symbol is first found in, starting from 'startenv'
    """
    env = startenv
    obj = None
    tryagain = True
    while tryagain:
        try:
            obj = env[symbol]
            tryagain = False
        except LookupError, knf:
            env = env.enclos()
            if env.rsame(rinterface.emptyenv):
                tryagain = False
            else:
                tryagain = True
    return conversion.ri2py(env)


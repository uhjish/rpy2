from rpy2.robjects.robject import RObjectMixin
import rpy2.rinterface as rinterface

getmethod = rinterface.baseNameSpaceEnv.get("getMethod")

require = rinterface.baseNameSpaceEnv.get('require')
require(rinterface.StrSexpVector(('methods', )),
        quiet = rinterface.BoolSexpVector((True, )))


class RS4(RObjectMixin, rinterface.SexpS4):

    def slotnames(self):
        return methods_env['slotNames']()

    
    @staticmethod
    def isclass(name):
        return methods_env['isClass'](name)


    def validobject(self, test = False, complete = False):
        return methods_env['validObject'](test = False, complete = False)



methods_env = rinterface.baseNameSpaceEnv.get('as.environment')(rinterface.StrSexpVector(('package:methods', )))

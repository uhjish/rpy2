from collections import namedtuple
from rpy2.robjects.packages import importr, data
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    dplyr = importr('dplyr', on_conflict="warn")
    TARGET_VERSION = '0.4.3'
    if dplyr.__version__ != TARGET_VERSION:
        warnings.warn('This was designed againt dplyr version %s but you have %s' % (TARGET_VERSION, dplyr.__version__))
    lazyeval = importr('lazyeval', on_conflict="warn")

    
from rpy2 import robjects

StringInEnv = namedtuple('StringInEnv', 'string env')
def _wrap_simple(rfunc, cls):
    """ Create a wrapper for `rfunc` that wrap its result in a call
    to the constructor of class `cls` """
    def func(*args, **kwargs):
    	return cls(rfunc(*args, **kwargs))
    return func

def _wrap(rfunc, cls, env=robjects.globalenv):
    def func(dataf, *args, **kwargs):
        args_inenv = list()
        for v in args:
            if isinstance(v, StringInEnv):
                args_inenv.append(lazyeval.as_lazy(v.string, env=v.env))
            else:
                args_inenv.append(lazyeval.as_lazy(v, env=env))
        kwargs_inenv = dict()
        for k,v in kwargs.items():
            if isinstance(v, StringInEnv):
                kwargs_inenv[k] = lazyeval.as_lazy(v.string, env=v.env)
            else:
                kwargs_inenv[k] = lazyeval.as_lazy(v, env=env)
        if cls is None:
            return type(dataf)(rfunc(dataf, *args_inenv, **kwargs_inenv))
        else:
            return cls(rfunc(dataf, *args_inenv, **kwargs_inenv))
    return func


def _make_pipe(rfunc, cls, env=robjects.globalenv):
    def func(*args, **kwargs):
        def func2(obj):
            args_inenv = list()
            for v in args:
                if isinstance(v, StringInEnv):
                    args_inenv.append(lazyeval.as_lazy(v.string, env=v.env))
                else:
                    args_inenv.append(lazyeval.as_lazy(v, env=env))
            kwargs_inenv = dict()
            for k,v in kwargs.items():
                if isinstance(v, StringInEnv):
                    kwargs_inenv[k] = lazyeval.as_lazy(v.string, env=v.env)
                else:
                    kwargs_inenv[k] = lazyeval.as_lazy(v, env=env)
            return cls(rfunc(obj, *args_inenv, **kwargs_inenv))
        return func2
    return func

class DataFrame(robjects.DataFrame):
    def __rshift__(self, other):
        return other(self)

    def copy_to(self, destination, name, **kwargs):
        """
        - destination: database
        - name: table name in the destination database
        """
        res = dplyr.copy_to(destination, self, name=name)
        return type(self)(res)
        
class GroupedDataFrame(robjects.DataFrame):
    pass

DataFrame.arrange = _wrap(dplyr.arrange_, None)
DataFrame.mutate = _wrap(dplyr.mutate_, None)
DataFrame.transmute = _wrap(dplyr.transmute_, None)
DataFrame.filter = _wrap(dplyr.filter_, None)
DataFrame.select = _wrap(dplyr.select_, None)
DataFrame.group_by = _wrap(dplyr.group_by_, GroupedDataFrame)
DataFrame.distinct = _wrap(dplyr.distinct_, None)
DataFrame.inner_join = _wrap(dplyr.inner_join, None)
DataFrame.left_join = _wrap(dplyr.left_join, None)
DataFrame.right_join = _wrap(dplyr.right_join, None)
DataFrame.full_join = _wrap(dplyr.full_join, None)
DataFrame.semi_join = _wrap(dplyr.semi_join, None)
DataFrame.anti_join = _wrap(dplyr.anti_join, None)
DataFrame.slice = _wrap(dplyr.slice_, None)

DataFrame.collect = _wrap_simple(dplyr.collect, DataFrame)

GroupedDataFrame.summarize = _wrap(dplyr.summarize_, None)
GroupedDataFrame.summarise = GroupedDataFrame.summarize

arrange = _make_pipe(dplyr.arrange_, DataFrame)
mutate = _make_pipe(dplyr.mutate_, DataFrame)
transmute = _make_pipe(dplyr.transmute_, DataFrame)
filter = _make_pipe(dplyr.filter_, DataFrame)
select = _make_pipe(dplyr.select_, DataFrame)
group_by = _make_pipe(dplyr.group_by_, DataFrame)
summarize = _make_pipe(dplyr.summarize_, DataFrame)
summarise = summarize
distinct = _make_pipe(dplyr.distinct_, DataFrame)
inner_join = _make_pipe(dplyr.inner_join, DataFrame)
left_join = _make_pipe(dplyr.left_join, DataFrame)
right_join = _make_pipe(dplyr.right_join, DataFrame)
full_join = _make_pipe(dplyr.full_join, DataFrame)
semi_join = _make_pipe(dplyr.semi_join, DataFrame)
anti_join = _make_pipe(dplyr.anti_join, DataFrame)
slice = _make_pipe(dplyr.slice_, DataFrame)


from collections import namedtuple
from six import with_metaclass
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

def _fix_args_inenv(args, env):
    args_inenv = list()
    for v in args:
        if isinstance(v, StringInEnv):
            args_inenv.append(lazyeval.as_lazy(v.string, env=v.env))
        else:
            args_inenv.append(lazyeval.as_lazy(v, env=env))
    return args_inenv

def _fix_kwargs_inenv(kwargs, env):
    kwargs_inenv = dict()
    for k,v in kwargs.items():
        if isinstance(v, StringInEnv):
            kwargs_inenv[k] = lazyeval.as_lazy(v.string, env=v.env)
        else:
            kwargs_inenv[k] = lazyeval.as_lazy(v, env=env)
    return kwargs_inenv

def _wrap(rfunc, cls, env=robjects.globalenv):
    def func(dataf, *args, **kwargs):
        args_inenv = _fix_args_inenv(args, env)
        kwargs_inenv = _fix_kwargs_inenv(kwargs, env)
        if cls is None:
            return type(dataf)(rfunc(dataf, *args_inenv, **kwargs_inenv))
        else:
            return cls(rfunc(dataf, *args_inenv, **kwargs_inenv))
    return func

def _wrap2(rfunc, cls, env=robjects.globalenv):
    def func(dataf_a, dataf_b, *args, **kwargs):
        args_inenv = _fix_args_inenv(args, env)
        kwargs_inenv = _fix_kwargs_inenv(kwargs, env)
        if cls is None:
            return type(dataf_a)(rfunc(dataf_a, dataf_b,
                                       *args_inenv, **kwargs_inenv))
        else:
            return cls(rfunc(dataf_a, dataf_b,
                             *args_inenv, **kwargs_inenv))
    return func

def _make_pipe(rfunc, cls, env=robjects.globalenv):
    def func(*args, **kwargs):
        def func2(obj):
            args_inenv = _fix_args_inenv(args, env)
            kwargs_inenv = _fix_kwargs_inenv(kwargs, env)
            return cls(rfunc(obj, *args_inenv, **kwargs_inenv))
        return func2
    return func

def _make_pipe2(rfunc, cls, env=robjects.globalenv):
    def func(*args, **kwargs):
        def func2(obj_a, obj_b):
            args_inenv = _fix_args_inenv(args, env)
            kwargs_inenv = _fix_kwargs_inenv(kwargs, env)
            return cls(rfunc(obj_a, obj_b, *args_inenv, **kwargs_inenv))
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

    def collect(self, *args, **kwargs):
        cls = type(self)
        return cls(rfunc(self, *args, **kwargs))
        
class GroupedDataFrame(robjects.DataFrame):
    pass

DataFrame.arrange = _wrap(dplyr.arrange_, None)
DataFrame.distinct = _wrap(dplyr.distinct_, None)
DataFrame.mutate = _wrap(dplyr.mutate_, None)
DataFrame.transmute = _wrap(dplyr.transmute_, None)
DataFrame.filter = _wrap(dplyr.filter_, None)
DataFrame.select = _wrap(dplyr.select_, None)
DataFrame.group_by = _wrap(dplyr.group_by_, GroupedDataFrame)
DataFrame.distinct = _wrap(dplyr.distinct_, None)
DataFrame.inner_join = _wrap2(dplyr.inner_join, None)
DataFrame.left_join = _wrap2(dplyr.left_join, None)
DataFrame.right_join = _wrap2(dplyr.right_join, None)
DataFrame.full_join = _wrap2(dplyr.full_join, None)
DataFrame.semi_join = _wrap2(dplyr.semi_join, None)
DataFrame.anti_join = _wrap2(dplyr.anti_join, None)
DataFrame.sample_n = _wrap(dplyr.sample_n, None)
DataFrame.sample_frac = _wrap(dplyr.sample_frac, None)
DataFrame.slice = _wrap(dplyr.slice_, None)

GroupedDataFrame.summarize = _wrap(dplyr.summarize_, DataFrame)
GroupedDataFrame.summarise = GroupedDataFrame.summarize

arrange = _make_pipe(dplyr.arrange_, DataFrame)
distinct = _make_pipe(dplyr.distinct_, DataFrame)
mutate = _make_pipe(dplyr.mutate_, DataFrame)
transmute = _make_pipe(dplyr.transmute_, DataFrame)
filter = _make_pipe(dplyr.filter_, DataFrame)
select = _make_pipe(dplyr.select_, DataFrame)
group_by = _make_pipe(dplyr.group_by_, DataFrame)
summarize = _make_pipe(dplyr.summarize_, DataFrame)
summarise = summarize
distinct = _make_pipe(dplyr.distinct_, DataFrame)
inner_join = _make_pipe2(dplyr.inner_join, DataFrame)
left_join = _make_pipe2(dplyr.left_join, DataFrame)
right_join = _make_pipe2(dplyr.right_join, DataFrame)
full_join = _make_pipe2(dplyr.full_join, DataFrame)
semi_join = _make_pipe2(dplyr.semi_join, DataFrame)
anti_join = _make_pipe2(dplyr.anti_join, DataFrame)
sample_n = _make_pipe(dplyr.sample_n, DataFrame)
sample_frac = _make_pipe(dplyr.sample_frac, DataFrame)
slice = _make_pipe(dplyr.slice_, DataFrame)



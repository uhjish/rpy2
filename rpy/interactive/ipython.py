""" Goodies for ipython """

from rpy2 import robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.lib import ggplot2

from IPython.core.display import Image

import tempfile

grdevices = importr('grDevices')

# automatic plotting of ggplot2 figures

class GGPlot(ggplot2.GGPlot):

    # special representation for ipython
    def _repr_png_(self, width = 600, height = 400):
        # Hack with a temp file (use buffer later ?)
        fn = tempfile.NamedTemporaryFile(mode = 'wb', suffix = '.png',
                                         delete = False)
        fn.close()
        grdevices.png(fn.name, width = width, height = height)
        self.plot()
        grdevices.dev_off()
        import io
        with io.OpenWrapper(fn.name, mode='rb') as data:
           res = data.read()
        return res

    def _repr_svg_(self, width = 6, height = 4):
        # Hack with a temp file (use buffer later ?)
        fn = tempfile.NamedTemporaryFile(mode = 'wb', suffix = '.svg',
                                         delete = False)
        fn.close()
        grdevices.svg(fn.name, width = width, height = height)
        self.plot()
        grdevices.dev_off()
        import io
        with io.OpenWrapper(fn.name, mode='rb') as data:
           res = data.read().decode('utf-8')
        return res

    def png(self, width = 600, height = 400):
        """ Build an Ipython "Image" (requires iPython). """
        return Image(self._repr_png_(width = width, height = height), 
                     embed=True)

    def svg(self, width = 6, height = 4):
        """ Build an Ipython "Image" (requires iPython). """
        return Image(self._repr_svg_(width = width, height = height), 
                     embed=True)

ggplot = GGPlot.new

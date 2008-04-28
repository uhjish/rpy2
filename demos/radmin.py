"""
A front-end to R's packags, and help/documentation systems
"""

import os
import pygtk
pygtk.require('2.0')
import gtk
import rpy2.robjects as robjects
import itertools
import gobject

class LibraryPanel(gtk.VBox):

    cell = gtk.CellRendererText()
    cell.set_property('cell-background', 'black')
    cell.set_property('foreground', 'white')
    PACKAGE_I = 0

    def __init__(self, console=None):
        super(LibraryPanel, self).__init__()
        self._console = console
        self._table = gtk.ListStore(str, str, str)
        self.updateInstalledLibraries()
        self._treeView = gtk.TreeView(model = self._table)
        self._treeView.show()
        self._valueColumns = [gtk.TreeViewColumn('Package'),
                              gtk.TreeViewColumn('Installed'),
                              gtk.TreeViewColumn('Available')]
        self._valueCells = []
        for col_i, col in enumerate(self._valueColumns):
            self._treeView.append_column(col)
            cr = gtk.CellRendererText()
            col.pack_start(cr, True)
            self._valueCells.append(cr)
            col.set_attributes(cr, text=col_i)
 
        sbox = gtk.HBox(homogeneous=False, spacing=0)
        sbox.show()
        slabel = gtk.Label("Search:")
        slabel.show()
        sbox.pack_start(slabel, True, True, 0)
        self.sentry = gtk.Entry()
        self.sentry.show()
        sbox.add(self.sentry)
        sbutton = gtk.Button("Refresh")
        sbutton.connect("clicked", self.searchAction, "search")
        sbutton.show()
        sbox.add(sbutton)
        self.pack_start(sbox, expand=False, fill=False, padding=0)
        s_window = gtk.ScrolledWindow()
        s_window.set_policy(gtk.POLICY_AUTOMATIC, 
                            gtk.POLICY_AUTOMATIC)
        s_window.show()
        s_window.add(self._treeView)
        self.add(s_window)
        
        lbox = gtk.HBox(homogeneous=False, spacing=0)
        lbox.show()
        lbutton = gtk.Button("Load")
        lbutton.connect("clicked", self.loadAction, "load")
        lbutton.show()
        lbox.add(lbutton)
        self.pack_start(lbox, expand=False, fill=False, padding=0)

    def updateInstalledLibraries(self):
        self._table.clear()
        installedLibraries = robjects.r["installed.packages"]()
        nrows = robjects.r.nrow(installedLibraries)[0]
        ncols = robjects.r.ncol(installedLibraries)[0]
        for i in range(1, nrows + 1):
            row = []
            pack = installedLibraries.subset(i, 1)._sexp[0]
            row.append(pack)
            pack = installedLibraries.subset(i, 3)._sexp[0]
            row.append(pack)
            pack = installedLibraries.subset(i, 4)._sexp[0]
            row.append(pack)
            self._table.append(row)

    def searchAction(self, widget, data=None):
        string = (self.sentry.get_text())
        self.updateInstalledLibraries()
        if string is None:
            return
        matches = robjects.r["help.search"](string).subset("matches")[0]
        spacks = [x for x in matches.subset(True, "Package")._sexp]
        spacks = set(spacks)
        toremove = []
        for ii, row in enumerate(self._table):
            if not (row[0] in spacks):
                toremove.append(ii)
        toremove.reverse()
        for r in toremove:
            self._table.remove(self._table.get_iter(r))

    def loadAction(self, widget, data=None):
        # Get the selection in the gtk.TreeView
	selection = self._treeView.get_selection()
	# Get the selection iter
	model, selection_iter = selection.get_selected()
        if selection_iter:
            packName = self._table.get_value(selection_iter, 
                                            self.PACKAGE_I)
            self._console.append('library("%s")\n' %packName)
            
            tmp = robjects.baseNameSpaceEnv["fifo"]("")
            robjects.baseNameSpaceEnv["sink"](tmp)
            
            robjects.baseNameSpaceEnv["library"](packName)

            out = robjects.baseNameSpaceEnv["readLines"](tmp)
            for line in out:
                self._console.append(str(line)+"\n")
            robjects.r.close(tmp)
            self._console.append("> ")

class VignetteExplorer(gtk.VBox):

    PACKAGE_I = 0
    ITEM_I = 1
    _vignettes = None

    def __init__(self):
        super(VignetteExplorer, self).__init__()
        self._table = gtk.ListStore(str, str, str)
        self.updateKnownVignettes()
        self._treeView = gtk.TreeView(model = self._table)
        self._treeView.show()
        self._valueColumns = [gtk.TreeViewColumn('Package'),
                              gtk.TreeViewColumn('Item'),
                              gtk.TreeViewColumn('Title')]
        self._valueCells = []
        for col_i, col in enumerate(self._valueColumns):
            self._treeView.append_column(col)
            cr = gtk.CellRendererText()
            col.pack_start(cr, True)
            self._valueCells.append(cr)
            col.set_attributes(cr, text=col_i)

        sbox = gtk.HBox(homogeneous=False, spacing=0)
        #sbox.show()
        sentry = gtk.Entry()
        sentry.show()
        sbox.add(sentry)
        sbutton = gtk.Button("Search")
        sbutton.show()
        sbox.add(sbutton)
        self.pack_start(sbox, expand=False, fill=False, padding=0)
        s_window = gtk.ScrolledWindow()
        s_window.set_policy(gtk.POLICY_AUTOMATIC, 
                            gtk.POLICY_AUTOMATIC)
        s_window.show()
        s_window.add(self._treeView)
        self.add(s_window)
        vbox = gtk.HBox(homogeneous=False, spacing=0)
        vbox.show()
        vbutton = gtk.Button("View")
        vbutton.connect("clicked", self.viewAction, "view")
        vbutton.show()
        vbox.add(vbutton)
        self.pack_start(vbox, expand=False, fill=False, padding=0)

    def updateKnownVignettes(self):
        self._table.clear()

        vignettes = robjects.r["vignette"]().subset("results")[0]

        nrows = robjects.baseNameSpaceEnv["nrow"](vignettes)[0]
        ncols = robjects.baseNameSpaceEnv["ncol"](vignettes)[0]
        for i in range(1, nrows + 1):
            row = []
            pack = vignettes.subset(i, 1)._sexp[0]
            row.append(pack)
            pack = vignettes.subset(i, 3)._sexp[0]
            row.append(pack)
            pack = vignettes.subset(i, 4)._sexp[0]
            row.append(pack)
            self._table.append(row)
        
        self._vignettes = vignettes

    def viewAction(self, widget, data=None):
        # Get the selection in the gtk.TreeView
	selection = self._treeView.get_selection()
	# Get the selection iter
	model, selection_iter = selection.get_selected()
        if selection_iter:
            packName = self._table.get_value(selection_iter, 
                                             self.PACKAGE_I)
            vigName = self._table.get_value(selection_iter, 
                                            self.ITEM_I)
            
            pdffile = robjects.r.vignette(vigName, package = packName)
            pdffile = pdffile.subset("file")[0][0]
            pdfviewer = robjects.baseNameSpaceEnv["options"]("pdfviewer")[0][0]

            pid = os.spawnl(os.P_NOWAIT, pdfviewer, pdffile)
            

class GraphicalDeviceExplorer(gtk.VBox):

    def __init__(self):
        super(GraphicalDeviceExplorer, self).__init__()
        self._table = gtk.ListStore(str, int, str, str)
        self.updateOpenedDevices()
        self._treeView = gtk.TreeView(model = self._table)
        self._treeView.show()
        self._valueColumns = [gtk.TreeViewColumn('Active'),
                              gtk.TreeViewColumn('Number'),
                              gtk.TreeViewColumn('Device'),
                              gtk.TreeViewColumn('Title')]
        self._valueCells = []
        for col_i, col in enumerate(self._valueColumns):
            self._treeView.append_column(col)
            cr = gtk.CellRendererText()
            col.pack_start(cr, True)
            self._valueCells.append(cr)
            col.set_attributes(cr, text=col_i)

        sbox = gtk.HBox(homogeneous=False, spacing=0)
        sbox.show()
        sentry = gtk.Entry()
        sentry.show()
        sbox.add(sentry)
        sbutton = gtk.Button("Refresh")
        sbutton.connect("clicked", self.searchOpenedDevices, "search")
        sbutton.show()
        sbox.add(sbutton)
        self.pack_start(sbox, expand=False, fill=False, padding=0)
        s_window = gtk.ScrolledWindow()
        s_window.set_policy(gtk.POLICY_AUTOMATIC, 
                            gtk.POLICY_AUTOMATIC)
        s_window.show()
        s_window.add(self._treeView)
        self.add(s_window)

    def updateOpenedDevices(self):
        self._table.clear()
        devices = robjects.r["dev.list"]()
        names = robjects.r["names"](devices)
        current_device = robjects.r["dev.cur"]()[0]
        try:
            nrows = len(devices)
        except:
            return
        for dev, name in itertools.izip(devices, names):
            if current_device == dev[0]:
                cur = "X"
            else:
                cur = ""
            row = [cur, dev[0], name[0], ""]
            self._table.append(row)

    def searchOpenedDevices(self, widget, data = None):
        self.updateOpenedDevices()
        
class HelpExplorer(gtk.VBox):

    def __init__(self):
        super(HelpExplorer, self).__init__()
        self._table = gtk.ListStore(str, str, str)
        self.updateRelevantHelp(None)
        self._treeView = gtk.TreeView(model = self._table)
        self._treeView.show()
        self._valueColumns = [gtk.TreeViewColumn('Topic'),
                              gtk.TreeViewColumn('Title'),
                              gtk.TreeViewColumn('Package'),]
        self._valueCells = []
        for col_i, col in enumerate(self._valueColumns):
            self._treeView.append_column(col)
            cr = gtk.CellRendererText()
            col.pack_start(cr, True)
            self._valueCells.append(cr)
            col.set_attributes(cr, text=col_i)
        self._treeView.connect('button_press_event', self.buttonAction)

        sbox = gtk.HBox(homogeneous=False, spacing=0)
        sbox.show()
        slabel = gtk.Label("Search:")
        slabel.show()
        sbox.pack_start(slabel, True, True, 0)
        self.sentry = gtk.Entry()
        self.sentry.show()
        sbox.add(self.sentry)
        fbutton = gtk.CheckButton("fuzzy")
        fbutton.show()
        sbox.pack_start(fbutton, expand=False, fill=False, padding=0)
        self._fuzzyButton = fbutton
        sbutton = gtk.Button("Refresh")
        sbutton.connect("clicked", self.searchAction, "search")

        sbutton.show()
        sbox.add(sbutton)
        self.pack_start(sbox, expand=False, fill=False, padding=0)
        s_window = gtk.ScrolledWindow()
        s_window.set_policy(gtk.POLICY_AUTOMATIC, 
                            gtk.POLICY_AUTOMATIC)
        s_window.show()
        s_window.add(self._treeView)
        self.add(s_window)

    def updateRelevantHelp(self, string):
        self._table.clear()
        if string is None:
            return
        agrep = [False, True][self._fuzzyButton.get_active()]
        matches = robjects.r["help.search"](string, agrep=agrep).subset("matches")[0]
        #import pdb; pdb.set_trace()
        nrows = robjects.r.nrow(matches)[0]
        ncols = robjects.r.ncol(matches)[0]
        for i in range(1, nrows + 1):
            row = []
            pack = matches.subset(i, 1)._sexp[0]
            row.append(pack)
            pack = matches.subset(i, 2)._sexp[0]
            row.append(pack)
            pack = matches.subset(i, 3)._sexp[0]
            row.append(pack)
            self._table.append(row)

    def searchAction(self, widget, data=None):
         self.updateRelevantHelp(self.sentry.get_text())

    def buttonAction(self, widget, data=None):
         treeselection = self._treeView.get_selection()
         (model, rowiter) = treeselection.get_selected()
         if rowiter is None:
             return
         #import pdb; pdb.set_trace()
         row = self._table[rowiter]
         helpFile = robjects.r.help(row[0], package=row[2])

class CodePanel(gtk.VBox):

    def __init__(self):
        super(CodePanel, self).__init__()
        label = gtk.Label("Enter R code to evaluate")
        label.show()
        self.pack_start(label, False, True, 0)
        s_window = gtk.ScrolledWindow()
        s_window.set_policy(gtk.POLICY_AUTOMATIC, 
                            gtk.POLICY_AUTOMATIC)
        s_window.show()
        self._rpad = gtk.TextView(buffer=None)
        self._rpad.set_editable(True)
        self._rpad.show()
        s_window.add(self._rpad)
        self.add(s_window)
        evalButton = gtk.Button("Evaluate")
        evalButton.connect("clicked", self.evaluateAction, "evaluate")
        evalButton.show()
        self.pack_start(evalButton, False, False, 0)
        self._evalButton = evalButton

    def evaluateAction(self, widget, data=None):
        buffer = self._rpad.get_buffer()
        start_iter = buffer.get_iter_at_offset(0)
        stop_iter = buffer.get_iter_at_offset(buffer.get_char_count())
        rcode = buffer.get_text(start_iter, stop_iter)
        res = robjects.r(rcode)
        

class EnvExplorer(gtk.VBox):
    def __init__(self, env):
        super(EnvExplorer, self).__init__()
        self._env = env
        self._table = gtk.ListStore(str, str)
        self.updateTable(None)
        self._treeView = gtk.TreeView(model = self._table)
        self._treeView.show()
        self._valueColumns = [gtk.TreeViewColumn('Symbol'),
                              gtk.TreeViewColumn('Type'),]
        self._valueCells = []
        for col_i, col in enumerate(self._valueColumns):
            self._treeView.append_column(col)
            cr = gtk.CellRendererText()
            col.pack_start(cr, True)
            self._valueCells.append(cr)
            col.set_attributes(cr, text=col_i)
        sbox = gtk.HBox(homogeneous=False, spacing=0)
        sbox.show()
        slabel = gtk.Label("Search:")
        slabel.show()
        sbox.pack_start(slabel, True, True, 0)
        self.sentry = gtk.Entry()
        self.sentry.show()
        sbox.add(self.sentry)
        sbutton = gtk.Button("Refresh")
        sbutton.connect("clicked", self.searchAction, "search")

        sbutton.show()
        sbox.add(sbutton)
        self.pack_start(sbox, expand=False, fill=False, padding=0)
        s_window = gtk.ScrolledWindow()
        s_window.set_policy(gtk.POLICY_AUTOMATIC, 
                            gtk.POLICY_AUTOMATIC)
        s_window.show()
        s_window.add(self._treeView)
        self.add(s_window)
        
    def updateTable(self, string):
        self._table.clear()
        
        for symbol in self._env: 
            stype = robjects.baseNameSpaceEnv["class"](self._env[symbol])
            row = [symbol, stype]
            self._table.append(row)

        if string is None:
            return

    def searchAction(self, widget, data=None):
        self.updateTable(None)

class ConsolePanel(gtk.VBox):

    def __init__(self):
        super(ConsolePanel, self).__init__()
        s_window = gtk.ScrolledWindow()
        s_window.set_policy(gtk.POLICY_AUTOMATIC, 
                            gtk.POLICY_AUTOMATIC)
        s_window.show()

        t_table = gtk.TextTagTable()
        
        tag_out=gtk.TextTag("output")
        tag_out.set_property("foreground","blue")
        tag_out.set_property("font","monospace 10")
        t_table.add(tag_out)
        
        tag_in=gtk.TextTag("input")
        tag_in.set_property("foreground","black")
        tag_in.set_property("font","monospace 10")
        t_table.add(tag_in)

        self._buffer = gtk.TextBuffer(t_table)
        self._view = gtk.TextView(buffer = self._buffer)
        self._view.connect("key_press_event", self.actionKeyPress)
        self._view.show()
        s_window.add(self._view)
        self.add(s_window)
        self.append("> ")

    def actionKeyPress(self, view, event):
        pass

    def append(self, text):
        pos=self._buffer.get_end_iter()
        self._buffer.insert(pos, text)

class Main(object):

    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        window.set_title("R")
        window.connect("delete_event", self.delete_event)
        window.connect("destroy", self.destroy)
        window.set_size_request(450, 500)

        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_LEFT)
        notebook.set_show_tabs(True)
        notebook.show()
        #vbox = gtk.VBox(homogeneous=False, spacing=0)
        #vbox.show()


        consolePanel = ConsolePanel()
        #tmp = robjects.baseNameSpaceEnv["fifo"]("")
        #robjects.baseNameSpaceEnv["sink"](tmp)
        
        #s = r.readLines(tmp)
        #r.close(tmp)
        #s = str.join(os.linesep, s._sexp)
        consolePanel.show()
        notebook.append_page(consolePanel, gtk.Label("Console"))

        codePanel = CodePanel()
        codePanel.show()
        notebook.append_page(codePanel, gtk.Label("Code"))

        # global env
        globalEnvPanel = EnvExplorer(robjects.globalEnv)
        globalEnvPanel.show()
        notebook.append_page(globalEnvPanel, gtk.Label("globalEnv"))

        # global env
        grDevPanel = GraphicalDeviceExplorer()
        grDevPanel.show()
        notebook.append_page(grDevPanel, gtk.Label("Graphics"))

        # libraries/packages
        libPanel = LibraryPanel(console=consolePanel)
        libPanel.show()
        notebook.append_page(libPanel, gtk.Label("Libraries"))

        # vignettes
        vigPanel = VignetteExplorer()
        vigPanel.show()
        notebook.append_page(vigPanel, gtk.Label("Vignettes"))

        # doc
        docPanel = HelpExplorer()
        docPanel.show()
        notebook.append_page(docPanel, gtk.Label("Documentation"))

        window.add(notebook)

        window.show()

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()


def get_splash():
    splash = gtk.Window(gtk.WINDOW_TOPLEVEL)
    splash.set_events(splash.get_events() | gtk.gdk.BUTTON_PRESS_MASK)
    def f(widget, data=None):
        splash.destroy()
    splash.connect('button_press_event', f)

    eb = gtk.EventBox()
    eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
    image = gtk.Image()
    image.show()
    image.set_from_file("rpy2_logo.png")
    splashVBox = gtk.VBox()

    splashVBox.pack_start(image, True, True, 0)
    splashVBox.pack_start(gtk.Label("A GTK+ toy user interface"), 
                          True, True, 0)
    eb.add(splashVBox)
    splash.add(eb)
    splash.realize()
    splash.window.set_type_hint (gtk.gdk.WINDOW_TYPE_HINT_SPLASHSCREEN)
    # needed on Win32
    splash.set_decorated (False)
    splash.set_position (gtk.WIN_POS_CENTER)
    return splash

def create_application(splash):
    w = Main()
    gtk.window_set_auto_startup_notification(True) 

gtk.window_set_auto_startup_notification(False) 
splash = get_splash()
splash.show_all()
gobject.idle_add(create_application, splash)
gtk.main()





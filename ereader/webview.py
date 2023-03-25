from queue import Queue
from typing import Callable

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QMouseEvent


class WebView(QWebEngineView):
    """
    A class representing a web view.
    """

    def __init__(self,parent:QWidget = None) -> None:
        """
        Initializes a new instance of the WebView class.
        """
        super().__init__(parent)
        self._loadFinishedQueue = Queue()
        self.loadFinished.connect(self._onLoadFinished)
        self.loadStarted.connect(self._onLoadStarted)
        self.loading = False

        self._childWidget = None
        self.installEventFilter(self)

    def runALF(self,func:Callable)->None:
        """
        runs a function After the web view's Loading Finished .
        """
        self._loadFinishedQueue.put(func)

    def runINL(self,func:Callable)->None:
        """
        runs a function if the web view Is Not Loading.
        """
        if not self.loading:
            func()

    def _onLoadStarted(self) -> None:
        self.loading = True

    def _onLoadFinished(self)->None:
        self.loading = False
        while not self._loadFinishedQueue.empty():
            self._loadFinishedQueue.get()()

    def eventFilter(self, source, event):
        """
        Make event handlers about mouse work.
        """
        if (event.type() == QEvent.ChildAdded and
            source is self and
            event.child().isWidgetType()):
            self._childWidget = event.child()
            self._childWidget.installEventFilter(self)
        elif (isinstance(event, QMouseEvent) and 
                         source is self._childWidget):
            if event.type() == QEvent.MouseButtonPress:
                self.mousePressEvent(event)
            elif event.type() == QEvent.MouseButtonRelease:
                self.mouseReleaseEvent(event)
            elif event.type() == QEvent.MouseMove:
                self.mouseMoveEvent(event)
            elif event.type() == QEvent.MouseButtonDblClick:
                self.mouseDoubleClickEvent(event)
        return super().eventFilter(source, event)

    



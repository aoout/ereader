from pathlib import Path

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class TocView(QTreeWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setHeaderHidden(True)
        self.hide()
        self.setMouseTracking(True)
        self.itemClicked.connect(self.onItemClicked)


    def load(self, toc:dict) -> None:
        self.clear()
        for item in toc:
            widgetItem = QTreeWidgetItem(self)
            widgetItem.setText(0, item["text"])
            widgetItem.url =  Path(str(item["url"]).split("#")[0])
            self.addTopLevelItem(widgetItem)
            for subitem in item.get("subitems",[]):
                subWidgetItem = QTreeWidgetItem(self)
                subWidgetItem.setText(0, subitem["text"])
                widgetItem.addChild(subWidgetItem)
                subWidgetItem.url = Path( str(subitem["url"]).split("#")[0])

    def onItemClicked(self, item:QTreeWidgetItem, column) -> None:
        pagesPath = self.parent().readView.epubParser.pagesPath
        self.parent().readView.loadPage(pagesPath.index(item.url))

    def mouseMoveEvent(self, event) -> None:
        self.parent().mouseMoveEvent(event)

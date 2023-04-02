from pathlib import Path

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class TocView(QTreeWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setHeaderHidden(True)
        self.hide()
        self.setMouseTracking(True)

        self.setIndentation(6)
        self.itemClicked.connect(self.onItemClicked)

    def load(self, toc: list) -> None:
        self.clear()

        def add_item(item, parent=None):
            widgetItem = QTreeWidgetItem(parent)
            widgetItem.setText(0, item["text"])
            widgetItem.url = Path(item["url"].split("#")[0])
            if parent is None:
                self.addTopLevelItem(widgetItem)
            else:
                parent.addChild(widgetItem)
            for subitem in item.get("subitems", []):
                add_item(subitem, widgetItem)

        for item in toc:
            add_item(item)

    def onItemClicked(self, item: QTreeWidgetItem, column) -> None:
        pagesPath = self.parent().readView.epubParser.pagesPath
        self.parent().readView.loadPage(pagesPath.index(item.url))

    def mouseMoveEvent(self, event) -> None:
        self.parent().mouseMoveEvent(event)

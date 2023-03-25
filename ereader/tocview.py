from PyQt5.QtWidgets import QTreeWidget,QTreeWidgetItem

class TocView(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.hide()
        self.setMouseTracking(True)
        self.itemClicked.connect(self.onItemClicked)

    def load(self, toc):
        self.clear()
        for item in toc:
            widgetItem = QTreeWidgetItem(self)
            widgetItem.setText(0, item["text"])
            widgetItem.url = item["url"]
            self.addTopLevelItem(widgetItem)
            for subitem in item.get("subitems",[]):
                subWidgetItem = QTreeWidgetItem(self)
                subWidgetItem.setText(0, subitem["text"])
                widgetItem.addChild(subWidgetItem)
                subWidgetItem.url = subitem["url"]

    def onItemClicked(self, item,column):
        pages_path = self.parent().readView.epubParser.pages_path
        self.parent().readView.loadPage(pages_path.index(item.url))

    def mouseMoveEvent(self, event):
        self.parent().mouseMoveEvent(event)

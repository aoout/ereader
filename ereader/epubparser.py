import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import List, Tuple

import xmltodict

class EpubParser:
    def __init__(self, filename: str) -> None:
        """
        Initialize EpubParser
        """
        self.filename = filename
        self.tempdir = Path(tempfile.TemporaryDirectory().name)
        self.currentPageIndex = 0
        self.extract()
        self.opfFile = next(Path(self.tempdir).rglob('content.opf'), None)
        self.tempdir = self.opfFile.parent

        self.pagesPath ,self.css_path = self.parse()
        self.toc = self.parseToc()

    def extract(self):
        if self.tempdir.exists():
            shutil.rmtree(self.tempdir)
        os.makedirs(self.tempdir)
        with zipfile.ZipFile(self.filename, 'r') as zipRef:
            zipRef.extractall(self.tempdir)

    def parse(self) -> Tuple[List[Path],List[Path]]:
        with open(self.opfFile, 'r', encoding='utf-8') as f:
            opfContent = f.read()

        opfDict = xmltodict.parse(opfContent)
        manifest = opfDict['package']['manifest']
        pages = [self.tempdir / item['@href'] for item in manifest['item'] if
                           item['@media-type'] == 'application/xhtml+xml']
        css = [self.tempdir /item['@href'] for item in manifest['item'] if item['@media-type'] == 'text/css']
        return pages,css

    def parseToc(self):
        tocFile = next(Path(self.tempdir).rglob('toc.ncx'), None)
        with open(tocFile, 'r', encoding='utf-8') as f:
            tocContent = f.read()

        tocDict = xmltodict.parse(tocContent)
        navMap = tocDict['ncx']['navMap']
        toc = []
        for item in navMap['navPoint']:
            tocItem = {'text': item['navLabel']['text'], 'url': self.tempdir / item['content']['@src']}
            if 'navPoint' in item:
                tocItem['subitems'] = []
                for subitem in item['navPoint']:
                    subitem = {'text': subitem['navLabel']['text'], 'url': self.tempdir / subitem['content']['@src']}
                    tocItem['subitems'].append(subitem)
            toc.append(tocItem)
        return toc

    def printToc(self):
        def printTocItem(item, level=0):
            print('  ' * level + item['text'])
            if 'subitems' in item:
                for subitem in item['subitems']:
                    printTocItem(subitem, level + 1)

        for item in self.toc:
            printTocItem(item)



    def currentPagePath(self) -> Path:
        return self.pagesPath[self.currentPageIndex]



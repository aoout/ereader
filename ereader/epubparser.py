import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import List, Tuple

import xmltodict


class EpubParser:
    def __init__(self, epubPath: str) -> None:
        """
        Initialize EpubParser
        """
        self.filename = epubPath
        self.tempDir = Path(tempfile.TemporaryDirectory().name)
        self.currentPageIndex = 0
        self.extract()
        self.opfFile = next(Path(self.tempDir).rglob('content.opf'), None)
        self.tempDir = self.opfFile.parent

        self.pagesPath ,self.css_path = self.parse()
        self.toc = self.parseToc()

    def extract(self) -> None:
        if self.tempDir.exists():
            shutil.rmtree(self.tempDir)
        os.makedirs(self.tempDir)
        with zipfile.ZipFile(self.filename, 'r') as zipRef:
            zipRef.extractall(self.tempDir)

    def parse(self) -> Tuple[List[Path],List[Path]]:
        with open(self.opfFile, 'r', encoding='utf-8') as f:
            opfContent = f.read()

        opfDict = xmltodict.parse(opfContent)
        manifest = opfDict['package']['manifest']
        pages = [self.tempDir / item['@href'] for item in manifest['item'] if
                           item['@media-type'] == 'application/xhtml+xml']
        css = [self.tempDir /item['@href'] for item in manifest['item'] if item['@media-type'] == 'text/css']
        return pages,css

    def parseToc(self) -> dict:
        tocFile = next(Path(self.tempDir).rglob('toc.ncx'), None)
        with open(tocFile, 'r', encoding='utf-8') as f:
            tocContent = f.read()

        tocDict = xmltodict.parse(tocContent)
        navMap = tocDict['ncx']['navMap']
        toc = []

        def parseNavPoint(navPoint):
            tocItem = {'text': navPoint['navLabel']['text'], 'url': self.tempDir / navPoint['content']['@src']}
            if 'navPoint' in navPoint:
                if isinstance(navPoint['navPoint'], list):
                    tocItem['subitems'] = []
                    for subitem in navPoint['navPoint']:
                        tocItem['subitems'].append(parseNavPoint(subitem))
                else:
                    tocItem['subitems'] = [parseNavPoint(navPoint['navPoint'])]
            return tocItem

            

        for item in navMap['navPoint']:
            toc.append(parseNavPoint(item))

        return toc

    def printToc(self) -> None:
        def printTocItem(item, level=0):
            print('  ' * level + item['text'])
            if 'subitems' in item:
                for subitem in item['subitems']:
                    printTocItem(subitem, level + 1)

        for item in self.toc:
            printTocItem(item)



    def currentPagePath(self) -> Path:
        return self.pagesPath[self.currentPageIndex]



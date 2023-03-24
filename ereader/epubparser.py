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
        self.current_page_index = 0
        self.extract()
        self.opf_file = next(Path(self.tempdir).rglob('content.opf'), None)
        self.tempdir = self.opf_file.parent

        self.pages_path ,self.css_path = self.parse()

    def extract(self):
        if self.tempdir.exists():
            shutil.rmtree(self.tempdir)
        os.makedirs(self.tempdir)
        with zipfile.ZipFile(self.filename, 'r') as zip_ref:
            zip_ref.extractall(self.tempdir)

    def parse(self) -> Tuple[List[Path],List[Path]]:


        with open(self.opf_file, 'r', encoding='utf-8') as f:
            opf_content = f.read()

        opf_dict = xmltodict.parse(opf_content)
        manifest = opf_dict['package']['manifest']
        pages = [self.tempdir / item['@href'] for item in manifest['item'] if
                           item['@media-type'] == 'application/xhtml+xml']
        css = [self.tempdir /item['@href'] for item in manifest['item'] if item['@media-type'] == 'text/css']
        return pages,css

    def currentPagePath(self) -> Path:
        return self.pages_path[self.current_page_index]



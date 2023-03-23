import os
import shutil
import tempfile
import zipfile
from functools import cached_property
from pathlib import Path
from typing import List,Tuple

import xmltodict


class EpubParser:
    def __init__(self, filename: str) -> None:
        """
        Initialize EpubParser
        """
        self.filename = filename
        self.tempdir = Path(tempfile.TemporaryDirectory().name)
        self.current_page_index = 0
        self.opf_file = self.tempdir / 'content.opf'
        self.pages_path ,self.css_path = self.parse()

    def parse(self) -> Tuple[List[str],List[str]]:
        if self.tempdir.exists():
            shutil.rmtree(self.tempdir)
        os.makedirs(self.tempdir)
        with zipfile.ZipFile(self.filename, 'r') as zip_ref:
            zip_ref.extractall(self.tempdir)

        with open(self.opf_file, 'r', encoding='utf-8') as f:
            opf_content = f.read()

        opf_dict = xmltodict.parse(opf_content)
        manifest = opf_dict['package']['manifest']
        pages = [self.tempdir / item['@href'] for item in manifest['item'] if
                           item['@media-type'] == 'application/xhtml+xml']
        pages.sort()
        css = [self.tempdir /item['@href'] for item in manifest['item'] if item['@media-type'] == 'text/css']
        return pages,css

    def get_page_content(self, index: int) -> str:
        """
        Get page content by index
        """
        with open(self.pages_path[index], 'r', encoding='utf-8') as f:
            page_content = f.read()
        return page_content


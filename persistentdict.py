import os
import pickle
from collections import UserDict

class PersistentDict(UserDict):
    """
    A dictionary that persists to disk.
    """

    def __init__(self, filename: str) -> None:
        """
        Initializes a new instance of the PersistentDict class.
        """
        self.filename = filename

        if os.path.exists(filename):
            with open(filename, "rb") as f:
                data = pickle.load(f)
                super().__init__(data)
        else:
            super().__init__()

    def save(self) -> None:
        """
        Saves the dictionary to disk.
        """
        with open(self.filename, "wb") as f:
            pickle.dump(self.data, f)


data = PersistentDict(os.path.expanduser("~//.ereader"))
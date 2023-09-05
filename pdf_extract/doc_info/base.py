from abc import ABC, abstractmethod
from typing import List, Dict
from collections import OrderedDict
import pandas


class DocumentInfo(ABC):
    MINIMUM_REF_LEN = 4

    @abstractmethod
    def get_sections(self) -> OrderedDict[str, List[str]]:
        raise NotImplementedError

    @abstractmethod
    def get_tables(self) -> List[pandas.DataFrame]:
        raise NotImplementedError

    @abstractmethod
    def get_references(self) -> List[str]:
        raise NotImplementedError







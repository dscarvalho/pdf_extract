from abc import ABC, abstractmethod
from typing import List, Tuple
import pandas


class DocumentInfo(ABC):
    MINIMUM_REF_LEN = 4

    @property
    @abstractmethod
    def title(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def sections(self) -> List[dict]:
        raise NotImplementedError

    @property
    @abstractmethod
    def tables(self) -> List[pandas.DataFrame]:
        raise NotImplementedError

    @property
    @abstractmethod
    def references(self) -> List[str]:
        raise NotImplementedError







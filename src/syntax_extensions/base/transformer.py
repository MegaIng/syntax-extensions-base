from abc import ABC, abstractmethod

from syntax_extensions.base.parser import Module


class ModuleTransformer(ABC):
    @abstractmethod
    def transform(self, module: Module) -> bool:
        raise NotImplementedError


from typing import Dict
from app.domain.base import DomainAdapter
from app.domain.recipes import RecipeDomainAdapter
from app.domain.adapters.structured_text import StructuredTextAdapter


class DomainRegistry:

    _registry = {
        "structured_text": StructuredTextAdapter(),
    }

    @classmethod
    def get_adapter(cls, name: str):
        adapter = cls._registry.get(name)
        if not adapter:
            raise ValueError(f"Unknown domain: {name}")
        return adapter



    @classmethod
    def register(cls, name: str, adapter: DomainAdapter):
        """
        Register new domain dynamically.
        """
        cls._registry[name] = adapter

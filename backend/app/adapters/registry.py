from typing import Type
from app.adapters.base import BaseAdapter
from app.core.enums import Provider


_adapter_registry: dict[str, Type[BaseAdapter]] = {}


def register_adapter(provider: Provider):
    """Decorator to register an adapter"""
    def decorator(cls: Type[BaseAdapter]) -> Type[BaseAdapter]:
        _adapter_registry[provider.value] = cls
        return cls
    return decorator


def get_adapter(provider: str) -> BaseAdapter | None:
    """Get an adapter instance by provider"""
    adapter_cls = _adapter_registry.get(provider)
    if adapter_cls:
        return adapter_cls()
    return None


def list_adapters() -> list[str]:
    """List all registered adapters"""
    return list(_adapter_registry.keys())
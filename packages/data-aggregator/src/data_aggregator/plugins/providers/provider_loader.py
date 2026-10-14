import logging
import pkgutil
from types import ModuleType
from typing import Any


class PluginRegistry:
  def __init__(self):
    self.plugins: dict[str, Any] = {}

  def register_plugin(self, provider_type: str, plugin: ModuleType):
    if provider_type in self.plugins:
      return
    self.plugins[provider_type] = plugin

  # def get(self, provider_type: str) -> ProviderPlugin:


class ProviderPluginLoader:
  registry = PluginRegistry()

  def __init__(self):
    self.registry = ProviderPluginLoader.registry
    self.logger = logging.getLogger(__name__)

  def load(self) -> PluginRegistry:

    for module_info in pkgutil.iter_modules():
      self.logger.debug("'%s/%s", module_info.name, module_info.ispkg)
      # module = importlib.import_module(module_info.name)
    return self.registry

from abc import ABC, abstractmethod

from .health_check_result import HealthCheckResult
from .provider_configuration import ProviderConfigurationBase


class HealthChecker[P: ProviderConfigurationBase](ABC):
  @abstractmethod
  async def check(self, provider: P) -> bool | HealthCheckResult:
    """Check the provider itself, independent of any source or target."""

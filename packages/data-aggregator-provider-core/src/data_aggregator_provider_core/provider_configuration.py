from abc import ABC
from typing import Annotated

from pydantic import BaseModel, Field

from .health_check_configuration import HealthCheckConfiguration


class ProviderConfigurationBase(BaseModel, ABC):
  # Filled by the aggregator from the key in the provider type section.
  # name: Annotated[str, Field(description="Unique provider name")]
  health_check: Annotated[
    HealthCheckConfiguration | object | None, Field(description="Health check definition")
  ] = None

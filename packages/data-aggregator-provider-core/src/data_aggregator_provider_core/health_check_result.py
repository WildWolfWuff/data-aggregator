from typing import Annotated

from pydantic import BaseModel, Field


class HealthCheckResult(BaseModel):
  healthy: Annotated[bool, Field(description="Whether the provider is reachable and usable")]
  message: Annotated[str, Field(description="Additional information about the check")] = ""

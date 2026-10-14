from typing import Annotated

from pydantic import BaseModel, Field


class HealthCheckConfiguration(BaseModel):
  timeout_seconds: Annotated[float, Field(gt=0, description="Health check timeout")] = 10.0

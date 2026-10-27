from typing import Annotated

from pydantic import BaseModel, Field

from .script.config import ScriptDataProcessorConfig


class AggregatorDataProcessingConfig(BaseModel):
  processing: Annotated[
    ScriptDataProcessorConfig, Field(discriminator="type", description="The processing configuration")
  ]

from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class ProviderReference(BaseModel):
  """Reference to a provider configuration, as `type:name` or `{"type": ..., "name": ...}`."""

  type: Annotated[str, Field(description="Provider type")]
  name: Annotated[str, Field(description="Provider name within the provider type section")]

  @model_validator(mode="before")
  @classmethod
  def _parse_short_form(cls, value: object) -> object:
    if not isinstance(value, str):
      return value
    provider_type, separator, name = value.partition(":")
    if not (separator and provider_type and name):
      raise ValueError(f"Provider reference '{value}' must have the form 'type:name'")
    return {"type": provider_type, "name": name}

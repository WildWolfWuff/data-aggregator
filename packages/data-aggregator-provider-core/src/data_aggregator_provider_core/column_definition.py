from typing import Annotated

from pydantic import BaseModel, Field, model_validator


class ColumnDefinition(BaseModel):
  """Column given as `name`, `name:type` or `{"name": ..., "type": ...}`."""

  name: Annotated[str, Field(description="Column name")]
  type: Annotated[str | None, Field(description="Column type, inferred from the data if unset")] = (
    None
  )

  @model_validator(mode="before")
  @classmethod
  def _parse_short_form(cls, value: object) -> object:
    if not isinstance(value, str):
      return value
    name, separator, column_type = value.partition(":")
    if not name or (separator and not column_type):
      raise ValueError(f"Column '{value}' must have the form 'name' or 'name:type'")
    return {"name": name, "type": column_type if separator else None}

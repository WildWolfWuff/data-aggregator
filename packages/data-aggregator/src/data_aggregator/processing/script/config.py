from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, FilePath, HttpUrl, SecretStr, model_validator

from .validation import DEFAULT_ALLOWED_MODULES


class BasicAuthConfig(BaseModel):
  type: Literal["basic"] = "basic"
  username: str
  password: SecretStr


class TokenAuthConfig(BaseModel):
  type: Literal["token"] = "token"
  token: SecretStr
  header: str = "Authorization"
  scheme: str | None = Field(default="Bearer", description="Prefix before the token; None sends the bare token")


type ScriptAuthConfig = Annotated[BasicAuthConfig | TokenAuthConfig, Field(discriminator="type")]


class ScriptDataProcessorConfig(BaseModel):
  type: Annotated[Literal["script"], Field(default="script", description="Type of the data processor (script)")]
  source: Annotated[HttpUrl | FilePath | None, Field(default=None, description="Source of the script")]
  content: Annotated[str | None, Field(default=None, description="Content of the script")]
  auth: Annotated[ScriptAuthConfig | None, Field(default=None, description="Authentication for a remote source")]
  allowed_modules: Annotated[
    frozenset[str], Field(default=frozenset(), description="Top-level modules the script may import")
  ]
  allow_http: Annotated[bool, Field(default=False, description="Permit plain http remote sources")]
  timeout: Annotated[float, Field(default=10.0, gt=0, description="Remote request timeout in seconds")]
  max_size_bytes: Annotated[int, Field(default=1_000_000, gt=0, description="Maximum script size in bytes")]

  @model_validator(mode="after")
  def _validate_origin(self) -> Self:
    self.allowed_modules = DEFAULT_ALLOWED_MODULES | self.allowed_modules
    if (self.source is None) == (self.content is None):
      raise ValueError("exactly one of 'source' or 'content' must be set")
    if self.auth is not None and not isinstance(self.source, HttpUrl):
      raise ValueError("'auth' is only supported for remote (http/https) sources")
    if isinstance(self.source, HttpUrl) and self.source.scheme == "http" and not self.allow_http:
      raise ValueError("plain http sources require 'allow_http'")
    return self

from pathlib import Path

from pydantic import BaseModel, Field


class ProviderPluginConfiguration(BaseModel):
  provider_plugin_folder: Path = Field(
    Path("/etc/aggregator/plugins"),
    description="Folder where additional provider plugins can be found",
  )

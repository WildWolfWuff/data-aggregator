from data_aggregator_provider_core import (
  Collector,
  CollectorConfigurationBase,
  Exporter,
  ExporterConfigurationBase,
  ProviderConfigurationBase,
  ProviderPlugin,
)


class FileProviderConfiguration(ProviderConfigurationBase):
  pass


class FileCollectorConfiguration(CollectorConfigurationBase):
  pass


class FileExporterConfiguration(ExporterConfigurationBase):
  pass


class FileExporter(Exporter[FileProviderConfiguration, FileExporterConfiguration]):
  pass


class FileCollector(Collector[FileProviderConfiguration, FileCollectorConfiguration]):
  pass


class FileProvider(ProviderPlugin):
  def __init__(self):
    super().__init__()

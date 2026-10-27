import hashlib
import importlib
import importlib.metadata
import json
import shutil
import site
import subprocess
import sys
import tempfile
from pathlib import Path

from .config import PluginsConfig

INSTALL_MARKER = ".aggregator-plugins.json"
PROTECTED_PREFIX = "data-aggregator"


class ProviderError(Exception):
  """Base class for provider related errors."""


class PluginLoadError(ProviderError):
  """Raised when plugins cannot be installed, loaded or validated."""

  def __init__(self, errors: list[str]) -> None:
    self.errors = errors
    super().__init__("Plugin loading failed:\n" + "\n".join(f"- {e}" for e in errors))


def _core_constraints() -> str:
  """Pin the running aggregator packages so plugins cannot replace them."""
  lines = sorted(
    {
      f"{d.metadata['Name']}=={d.version}"
      for d in importlib.metadata.distributions()
      if (d.metadata["Name"] or "").lower().startswith(PROTECTED_PREFIX)
    }
  )
  return "\n".join(lines) + "\n"


def _fingerprint(config: PluginsConfig) -> str:
  return hashlib.sha256(
    json.dumps(
      [
        config.model_dump(mode="json", include={"packages", "index_url", "no_index", "find_links"}),
        _core_constraints(),
      ],
      sort_keys=True,
    ).encode()
  ).hexdigest()


def install_plugins(config: PluginsConfig) -> None:
  """Install the configured packages into ``install_dir``; raises PluginLoadError on failure."""
  if not config.packages:
    return
  target = config.install_dir
  marker = target / INSTALL_MARKER
  fingerprint = _fingerprint(config)
  if marker.exists() and json.loads(marker.read_text()).get("fingerprint") == fingerprint:
    return

  installer = shutil.which("uv")
  with tempfile.TemporaryDirectory() as tmp:
    requirements = Path(tmp) / "requirements.txt"
    constraints = Path(tmp) / "constraints.txt"
    requirements.write_text(
      "".join(f"{p.name}" + (f" --hash=sha256:{p.sha256}" if p.sha256 else "") + "\n" for p in config.packages)
    )
    constraints.write_text(_core_constraints())
    base = [installer, "pip"] if installer else [sys.executable, "-m", "pip"]
    cmd = [*base, "install", "--target", str(target), "-r", str(requirements), "-c", str(constraints)]
    if installer:
      cmd += ["--python", sys.executable]
    if any(p.sha256 for p in config.packages):
      cmd.append("--require-hashes")
    if config.index_url:
      cmd += ["--index-url", config.index_url]
    if config.no_index:
      cmd.append("--no-index")
    for link in config.find_links:
      cmd += ["--find-links", link]
    target.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
  if result.returncode != 0:
    raise PluginLoadError([f"Plugin installation failed:\n{result.stdout}\n{result.stderr}".strip()])
  marker.write_text(json.dumps({"fingerprint": fingerprint}))


def add_plugin_paths(config: PluginsConfig) -> None:
  """Make installed and mounted plugins importable and discoverable."""
  for path in (config.install_dir, config.plugin_dir):
    if path and path.is_dir():
      site.addsitedir(str(path))
  importlib.invalidate_caches()

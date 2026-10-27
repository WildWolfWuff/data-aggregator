class ScriptError(Exception):
  """Base class for script processor errors."""


class ScriptLoadError(ScriptError):
  """The script source could not be loaded."""


class ScriptValidationError(ScriptError):
  """The script failed static validation."""

  def __init__(self, violations: list[str]) -> None:
    super().__init__("; ".join(violations))
    self.violations = violations


class ScriptExecutionError(ScriptError):
  """The script failed while running or returned an invalid result."""

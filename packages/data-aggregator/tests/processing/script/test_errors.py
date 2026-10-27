from data_aggregator.processing.script import ScriptValidationError


def test_validation_error_preserves_violations() -> None:
  violations = ["invalid import", "missing aggregate_data"]

  error = ScriptValidationError(violations)

  assert error.violations == violations
  assert str(error) == "invalid import; missing aggregate_data"
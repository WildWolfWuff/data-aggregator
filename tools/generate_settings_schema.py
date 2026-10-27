import json
from pathlib import Path

import click

from data_aggregator.settings import AggregatorSettings


@click.command()
@click.option(
  "--output",
  "-o",
  type=click.Path(dir_okay=False, writable=True, path_type=Path),
  default=None,
  help="File to write the schema to. Defaults to stdout.",
)
@click.option("--indent", type=click.IntRange(min=0), default=2, show_default=True, help="JSON indentation.")
def main(output: Path | None, indent: int) -> None:
  """Generate the JSON schema for AggregatorSettings."""
  # Class-level call; instantiating would make pydantic-settings parse sys.argv.
  schema = json.dumps(AggregatorSettings.model_json_schema(), indent=indent) + "\n"
  if output is None:
    click.echo(schema, nl=False)
  else:
    output.write_text(schema, encoding="utf-8")


if __name__ == "__main__":
  main()

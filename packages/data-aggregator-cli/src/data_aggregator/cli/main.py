from asyncio import run

from data_aggregator.aggregator import execute_aggregator


def main() -> None:
  run(execute_aggregator())


if __name__ == "__main__":
  main()

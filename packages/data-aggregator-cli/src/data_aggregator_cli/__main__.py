import asyncio
import logging
import sys

logging.basicConfig(
  level=logging.DEBUG,
  format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
  handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("aggregator.log")],
)


def main():
  from data_aggregator.app import Aggregator

  aggregator = Aggregator()
  asyncio.run(aggregator.execute_async())


if __name__ == "__main__":
  main()

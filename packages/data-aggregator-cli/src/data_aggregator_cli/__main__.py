import asyncio

from data_aggregator.app import Aggregator


def main():

  aggregator = Aggregator()
  asyncio.run(aggregator.execute())


if __name__ == "__main__":
  main()

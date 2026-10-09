import importlib


def test_package_is_importable() -> None:
    assert (
        importlib.import_module("data_aggregator_provider_grpc").__name__
        == "data_aggregator_provider_grpc"
    )

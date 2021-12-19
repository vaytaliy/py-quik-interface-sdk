import pytest


def test_import():
    """Can be imported."""
    import qlua

    assert (str(type(qlua.rpc.isConnected_pb2.Result()))
            == "<class 'qlua.rpc.isConnected_pb2.Result'>")

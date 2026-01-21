from dataclasses import FrozenInstanceError

import pytest

import data_on_chain as doc


def test_upload_data_creates_chain_with_single_block() -> None:
    chain = doc.upload_data("hello world")

    blocks = chain.blocks
    assert len(blocks) == 1
    block = blocks[0]

    assert block.index == 0
    assert block.data == "hello world"
    assert block.prev_hash == "GENESIS"
    assert isinstance(block.hash, str)
    assert len(block.hash) > 0


def test_chain_is_append_only_and_hash_linked() -> None:
    chain = doc.DemoBlockchain()
    first = chain.add_data("first")
    second = chain.add_data("second")

    assert second.index == first.index + 1
    assert second.prev_hash == first.hash

    assert chain.get_block(first.hash) == first
    assert chain.get_block(second.hash) == second


def test_block_is_immutable() -> None:
    chain = doc.upload_data("immutable data")
    block = chain.blocks[0]

    with pytest.raises(FrozenInstanceError):
        block.data = "modified"  # type: ignore[misc]


def test_retrieving_nonexistent_block_returns_none() -> None:
    chain = doc.DemoBlockchain()

    result = chain.get_block("nonexistent-hash")
    assert result is None

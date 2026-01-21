"""Simple in-memory blockchain-like demo for immutable data storage.

This is only for demonstration and testing purposes.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Block:
    index: int
    data: str
    prev_hash: str
    hash: str


class DemoBlockchain:
    """A minimal append-only chain using content hashing.

    Each new block includes the hash of the previous block, forming
    a simple immutable chain once created.
    """

    def __init__(self) -> None:
        self._blocks: List[Block] = []
        self._by_hash: Dict[str, Block] = {}

    @staticmethod
    def _compute_hash(index: int, data: str, prev_hash: str) -> str:
        payload = f"{index}|{data}|{prev_hash}".encode("utf-8")
        return sha256(payload).hexdigest()

    def add_data(self, data: str) -> Block:
        index = len(self._blocks)
        prev_hash = self._blocks[-1].hash if self._blocks else "GENESIS"
        block_hash = self._compute_hash(index=index, data=data, prev_hash=prev_hash)
        block = Block(index=index, data=data, prev_hash=prev_hash, hash=block_hash)
        self._blocks.append(block)
        self._by_hash[block.hash] = block
        return block

    def get_block(self, block_hash: str) -> Optional[Block]:
        return self._by_hash.get(block_hash)

    @property
    def blocks(self) -> List[Block]:
        return list(self._blocks)


def upload_data(data: str) -> DemoBlockchain:
    """Create a new demo chain with a single block containing the data.

    This acts as a simple example "upload" operation.
    """

    chain = DemoBlockchain()
    chain.add_data(data)
    return chain

from __future__ import annotations

"""Solana utilities for preparing on-chain uploads of data hashes.

This module focuses on *building* transactions and instructions only.
It does not send transactions or require network access, so it is safe
for use in unit tests without hitting a real Solana cluster.
"""

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Dict, List, Tuple

from solana.publickey import PublicKey
from solana.transaction import Transaction, TransactionInstruction

# Memo v2 program id (standard on Solana mainnet/devnet)
MEMO_PROGRAM_ID = PublicKey("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")


@dataclass(frozen=True)
class SolanaUploadPlan:
    """Plan for uploading a hash of some data to Solana via a Memo instruction.

    This is a pure data object describing what would be sent on-chain.
    """

    data_hash: str
    payer: PublicKey
    transaction: Transaction


def compute_data_hash(data: bytes) -> str:
    """Return SHA-256 hex digest of ``data``."""

    return sha256(data).hexdigest()


def hash_data_to_memo_instruction(data: bytes) -> Tuple[str, TransactionInstruction]:
    """Create a Memo instruction that carries the hash of ``data``.

    Returns a tuple of (hash_hex, instruction).
    No network calls are made.
    """

    hash_hex = compute_data_hash(data)
    memo_bytes = hash_hex.encode("utf-8")

    ix = TransactionInstruction(
        program_id=MEMO_PROGRAM_ID,
        keys=[],  # Memo program does not require any accounts
        data=memo_bytes,
    )
    return hash_hex, ix


def build_upload_transaction(payer: PublicKey, data: bytes) -> SolanaUploadPlan:
    """Build an unsigned Solana transaction with a Memo carrying the data hash.

    The resulting :class:`SolanaUploadPlan` can be used by caller code to sign
    and submit the transaction using their preferred client and key management.
    """

    hash_hex, ix = hash_data_to_memo_instruction(data)

    tx = Transaction()
    tx.fee_payer = payer
    tx.add(ix)

    return SolanaUploadPlan(data_hash=hash_hex, payer=payer, transaction=tx)

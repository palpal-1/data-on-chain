import data_on_chain as doc

from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction


def test_compute_data_hash_matches_sha256() -> None:
    data = b"hello solana"
    h1 = doc.compute_data_hash(data)

    # Compute directly to cross-check
    import hashlib

    h2 = hashlib.sha256(data).hexdigest()

    assert h1 == h2


def test_hash_data_to_memo_instruction_builds_memo_ix() -> None:
    data = b"example payload"
    expected_hash = doc.compute_data_hash(data)

    hash_hex, ix = doc.hash_data_to_memo_instruction(data)

    assert hash_hex == expected_hash
    assert isinstance(ix, TransactionInstruction)

    # Program id should be the standard Memo program
    assert ix.program_id == doc.MEMO_PROGRAM_ID

    # Data should be the UTF-8 encoding of the hash hex string
    assert ix.data == expected_hash.encode("utf-8")


def test_build_upload_transaction_wraps_memo_in_transaction() -> None:
    payer = PublicKey(0)  # dummy public key
    data = b"payload for transaction"

    plan = doc.build_upload_transaction(payer=payer, data=data)

    assert plan.payer == payer
    assert plan.data_hash == doc.compute_data_hash(data)

    tx = plan.transaction

    # Fee payer should be set
    assert tx.fee_payer == payer

    # Transaction should contain exactly one instruction, the memo
    assert len(tx.instructions) == 1
    ix = tx.instructions[0]
    assert ix.program_id == doc.MEMO_PROGRAM_ID
    assert ix.data == plan.data_hash.encode("utf-8")

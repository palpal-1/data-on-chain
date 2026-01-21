# data_on_chain

Utilities and demos for storing data (or data hashes) on-chain.

This project currently focuses on two things:

- An **in-memory demo blockchain** (`DemoBlockchain`) to illustrate append-only, immutable data.
- A **Solana helper** (`solana_uploader`) for building transactions that put a **SHA-256 hash** of your data on the Solana blockchain via the Memo program.

---

## 1. Installation

From the project root:

```bash
poetry install
```

This will install all Python dependencies, including `solana` (solana-py).

---

## 2. Concept: storing data on Solana

Instead of putting large blobs of data directly into Solana account storage, this project uses the following pattern:

- Compute a **SHA-256 hash** of your data off-chain.
- Put that **hash** into a **Memo instruction** in a Solana transaction.
- Submit the transaction to Solana (e.g. devnet), so the hash and transaction signature become immutable, public evidence that the data existed.

Your original data can live anywhere (database, S3, IPFS, etc.). You only need the data and the on-chain hash to re-verify integrity.

---

## 3. Solana helper API

The main Solana utilities live in `data_on_chain.solana_uploader` and are re-exported from the package root.

```python
import data_on_chain as doc

from solana.publickey import PublicKey


data = b"hello solana"

# 1) Compute the SHA-256 hash of the data
hash_hex = doc.compute_data_hash(data)

# 2) Build a Memo instruction that carries the hash
hash_hex2, ix = doc.hash_data_to_memo_instruction(data)
assert hash_hex2 == hash_hex

# 3) Build an unsigned transaction that contains this Memo instruction
payer = PublicKey(0)  # dummy payer for illustration
plan = doc.build_upload_transaction(payer=payer, data=data)

print("Data hash:", plan.data_hash)
print("Payer:", plan.payer)
print("Transaction:", plan.transaction)
```

Important notes:

- **No network calls** are made by these helpers.
- The resulting `SolanaUploadPlan` contains an **unsigned** transaction.
- You are responsible for providing a real `payer` and for signing/sending the transaction in your own code when you actually want to hit a Solana cluster.

---

## 4. Sending the transaction on Solana devnet

> **Warning**  
> The following code will **send a real transaction** when you fill in a valid keypair and RPC URL. Use **devnet** and test keys only.

Example script (not part of the library) to send the transaction on **Solana devnet**:

```python
from solana.keypair import Keypair
from solana.rpc.api import Client

import data_on_chain as doc


def main() -> None:
    # Configure RPC client (devnet)
    client = Client("https://api.devnet.solana.com")

    # Load or generate a keypair (DO NOT hardcode real secrets in source)
    # Here we just generate a new random keypair for demonstration.
    keypair = Keypair()
    payer = keypair.public_key

    content = b"my important data"

    # Build an unsigned transaction with a Memo instruction
    plan = doc.build_upload_transaction(payer=payer, data=content)

    # Fill recent_blockhash and sign
    latest = client.get_latest_blockhash()["result"]["value"]["blockhash"]
    tx = plan.transaction
    tx.recent_blockhash = latest
    tx.sign(keypair)

    # Send the transaction
    sig = client.send_raw_transaction(tx.serialize())["result"]

    print("Data hash:", plan.data_hash)
    print("Signature:", sig)
    print("Explorer (devnet): https://explorer.solana.com/tx/" + sig + "?cluster=devnet")


if __name__ == "__main__":
    main()
```

### Security and cost considerations

- Always use **test keys** and **devnet** for experiments.
- Never commit private keys or RPC URLs with embedded secrets.
- Use environment variables, `.env` files (excluded from git), or a secret manager.
- Each transaction costs a small amount of SOL (very cheap on devnet, but still real on mainnet).

---

## 5. In-memory demo blockchain

In addition to the Solana utilities, the project includes a simple in-memory demo blockchain, exported from `data_on_chain`:

```python
import data_on_chain as doc


# Create a simple in-memory chain and store some data
chain = doc.upload_data("hello world")
block = chain.blocks[0]

print(block.index, block.data, block.prev_hash, block.hash)
```

This is purely a teaching / demonstration tool to illustrate append-only, immutable structures. It does not talk to any real blockchain.


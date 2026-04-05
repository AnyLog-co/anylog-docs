---
title: Blockchain & Metadata
description: Manage the AnyLog metadata layer — query and update policies, configure master nodes, and optionally connect to a real blockchain.
layout: page
---

AnyLog uses a shared metadata layer called the **blockchain** to store all network policies: node configurations, cluster assignments, table schemas, permissions, and more. All metadata commands use the `blockchain` keyword regardless of whether the underlying store is a master node or a real blockchain platform.

> **Note:** The blockchain commands apply to both EdgeLake (master node only) and AnyLog (master node or real blockchain). See [Introduction — EdgeLake vs AnyLog](/docs/introduction/#edgelake-vs-anylog).

---

## Key concepts

- **Policy** — a JSON structure describing a node, cluster, table, or configuration. All metadata is stored as policies.
- **Master node** — an AnyLog instance that stores a copy of all policies in a local database. Simpler to operate; no crypto required.
- **Real blockchain** — AnyLog supports Layer-2 platforms (Optimism/Ethereum) for fully decentralised metadata without a single point of failure.
- **Local copy** — every node maintains a local copy of the blockchain, synced periodically via the [blockchain sync service](/docs/background-services/#blockchain-sync-service).

---

## Querying policies

```anylog
blockchain get [policy type] [where condition] [bring expression]
```

The `bring` clause extracts specific fields from matching policies.

| Example | Description |
|---|---|
| `blockchain get *` | Return all policies |
| `blockchain get operator` | All operator policies |
| `blockchain get operator where dbms = lsl_demo` | Operators for a specific database |
| `blockchain get (master, operator, query) bring.table [*][*][name] [*][ip] [*][port]` | Node summary table |
| `blockchain get cluster where table[dbms] = mydb bring [cluster][id] separator = ,` | Cluster IDs for a database |
| `blockchain get * bring.table.unique [*]` | Unique policy types |
| `blockchain get table where dbms = mydb bring [*][name] separator = \n` | Table names in a database |

---

## Adding a policy

```anylog
<blockchain insert where
  policy = [policy] and
  local = [true/false] and
  master = [IP:Port]>
```

Or for a real blockchain platform:
```anylog
blockchain insert where policy = !policy and local = true and blockchain = ethereum
```

### Policy structure

```anylog
<new_policy = {
  "policy_type": {
    "name": "my-node",
    "company": "AnyLog Co.",
    "ip": "10.0.0.1",
    "port": 32048
  }
}>

blockchain insert where policy = !new_policy and local = true and master = !master_node
```

When inserted, the network automatically adds `id` (unique hash) and `date` attributes.

---

## Deleting a policy

```anylog
blockchain delete policy where id = [policy id] and master = [IP:Port] and local = true
```

For blockchain:
```anylog
blockchain delete policy where id = [policy id] and local = true and blockchain = ethereum
```

> **Note:** Policies on a real blockchain are non-mutable. AnyLog uses [ANMP policies](https://github.com/AnyLog-co/documentation/blob/master/policies.md) to handle updates to node configuration without altering the original policy.

---

## Seeding metadata

Pull a fresh copy of the metadata from a peer node — useful when setting up a new node or connecting to a different network:

```anylog
blockchain seed from [ip:port]
```

Example:
```anylog
blockchain seed from 73.202.142.172:7848
```

When properly configured, the [blockchain sync service](/docs/background-services/#blockchain-sync-service) handles this continuously.

---

## Master node setup

If using a master node instead of a real blockchain:

```anylog
# Associate a physical database with the logical 'blockchain' database first
connect dbms blockchain where type = sqlite

# Create the ledger table
blockchain create table
```

Restore a master node from a backup file:
```anylog
blockchain update dbms [path/to/blockchain.json]
```

Validate the local ledger:
```anylog
blockchain test
```

Delete the local ledger file:
```anylog
blockchain delete local file
```

---

## Real blockchain (Optimism / Layer-2)

AnyLog supports the **Optimism** Layer-2 blockchain (built on Ethereum) for fully decentralised metadata. Optimism uses **rollups** — batching multiple transactions into one — bringing transaction costs from tens of dollars down to fractions of a cent.

**Key terms:**
- **Layer-2** — sits on top of Ethereum, inheriting its security at lower cost
- **Optimism** — AnyLog's default blockchain platform
- **Sepolia** — Optimism's test network
- **Infura** — the RPC provider used to connect to Optimism
- **Smart contract** — the on-chain store for AnyLog metadata. One contract per network is sufficient.

### Configuration parameters

| Parameter | Default | Description |
|---|---|---|
| `BLOCKCHAIN_SOURCE` | `master` | `master` = use master node; anything else = use the blockchain |
| `BLOCKCHAIN_DESTINATION` | — | Where to store the local blockchain copy |
| `SYNC_TIME` | 30 seconds | How often to sync from the blockchain |
| `PROVIDER` | `infura` | RPC provider |
| `PLATFORM` | `optimism` | Blockchain platform |
| `CONTRACT` | AnyLog default | Smart contract ID. Use the shared AnyLog contract or deploy your own. |
| `PRIVATE_KEY` / `PUBLIC_KEY` | — | Crypto wallet keys |
| `CHAIN_ID` | — | Wallet chain ID |

### Connect to Optimism (Sepolia testnet)

```anylog
platform = optimism
provider = infura

blockchain connect to !platform where provider = !provider
```

### Create a wallet (first time only)

```anylog
blockchain create account !platform

print !public_key
print !private_key
```

Save both keys securely. Add them to your node configuration for future restarts.

### Load wallet and set chain ID

```anylog
chain_id = 71143311

<blockchain set account info where
  platform = !platform and
  private_key = !private_key and
  public_key = !public_key and
  chain_id = !chain_id>
```

Verify:
```anylog
get platforms
```

### Deploy a smart contract

Only needed once per network. All nodes in the network share a single contract.

```anylog
contract = blockchain deploy contract where platform = optimism and public_key = !public_key

print !contract
```

Associate the contract with your account:
```anylog
blockchain set account info where platform = !platform and contract = !contract
```

To auto-create a contract on first run, set `CONTRACT=generate` in your configuration. After creation, update all node configs with the new contract ID.

### Enable continuous blockchain sync

```anylog
blockchain_source = blockchain

run blockchain sync where source = blockchain and time = !sync_time and dest = file and platform = optimism
```

---

## Monitoring

```anylog
blockchain test                  # validate local ledger structure
get metadata version             # current metadata version ID on this node
blockchain query metadata        # visualise data distribution across the network
test network metadata            # compare metadata version across all nodes
```
---
title: Background Services
description: Enable and monitor the core services that run on each AnyLog node — TCP, REST, operator, broker, Kafka, scheduler, and more.
layout: page
---

Services can be enabled in any of the following ways:
- Command line arguments when starting AnyLog
- Directly on the AnyLog CLI
- A script file processed with: `process [path/file]`
- A configuration policy associated with the node

List all services and their current status:
```anylog
get processes
get processes where format = json
```

---

## Network connectivity

Joining the AnyLog network requires two services: the **TCP service** (peer communication) and the **blockchain sync service** (metadata).

### TCP service

Enables AnyLog's peer-to-peer protocol for sending and receiving messages between nodes.

```anylog
<run tcp server where
  external_ip = [ip] and external_port = [port] and
  internal_ip = [local_ip] and internal_port = [local_port] and
  bind = [true/false] and threads = [count]>
```

- `threads` — number of worker threads handling incoming requests (default: 6)
- Use `internal_ip`/`internal_port` when the node is behind NAT or has separate LAN/WAN addresses

Examples:
```anylog
run tcp server where external_ip = !ip and external_port = !port and threads = 3

<run tcp server where
  external_ip = !external_ip and external_port = 7850 and
  internal_ip = !ip and internal_port = 7850 and
  bind = false and threads = 6>
```

Check connection info:
```anylog
get connections
```

### Blockchain sync service

Continuously pulls the latest metadata from the blockchain or master node and updates the local copy.

```anylog
run blockchain sync where source = [master|blockchain] and time = [interval] and dest = [file|dbms] and connection = [ip:port]
```

| Option | Description |
|---|---|
| `source` | `master` — use a master node; `blockchain` — use a blockchain platform |
| `dest` | `file` — store locally as JSON; `dbms` — store in a local database |
| `connection` | IP:Port of the master node (when `source = master`) |
| `time` | Sync frequency (e.g. `30 seconds`, `1 minute`) |

Examples:
```anylog
run blockchain sync where source = master and time = 30 seconds and dest = file and connection = !master_node
run blockchain sync where source = blockchain and time = !sync_time and dest = file and platform = optimism
```

Check sync status:
```anylog
get synchronizer
```

Switch to a different master node at runtime:
```anylog
blockchain switch network where master = [IP:Port]
```

---

## Operator service (local data storage)

The Operator service monitors the watch directory, identifies or creates schemas, and ingests data into local databases.

```anylog
run operator where [option] = [value] and ...
```

| Option | Description |
|---|---|
| `policy` | ID of the operator policy |
| `create_table` | `true` — auto-create tables if they don't exist |
| `update_tsd_info` | `true` — update the TSD summary table (used for HA sync) |
| `archive_json` | `true` — archive JSON files after processing |
| `archive_sql` | `true` — archive SQL files after processing |
| `compress_json` | `true/false` |
| `compress_sql` | `true/false` |
| `limit_tables` | Comma-separated list of table names to process |
| `master_node` | IP:Port of the master node |
| `distributor` | `true` — enable HA data distribution to peer operators |
| `threads` | Worker thread count |

Examples:
```anylog
run operator where create_table = true and update_tsd_info = true and archive_json = true and distributor = true and master_node = !master_node and policy = !operator_policy and threads = 3
```

Monitor the operator:
```anylog
get operator
get operator inserts
get operator summary
get operator config
get operator summary where format = json
```

---

## REST service

Enables HTTP-based communication from external applications and data sources.

```anylog
<run rest server where
  external_ip = [ip] and external_port = [port] and
  internal_ip = [local_ip] and internal_port = [local_port] and
  timeout = [seconds] and ssl = [true/false] and bind = [true/false]>
```

- `timeout` — max wait in seconds (0 = no limit, default: 20)
- `ssl = true` — enable HTTPS
- `bind = true` — only accept connections on the specified IP

Example:
```anylog
<run rest server where
  internal_ip = !ip and internal_port = 7849 and
  timeout = 0 and threads = 6 and ssl = false>
```

Monitor the REST service:
```anylog
get rest server info    # configuration
get rest calls          # request statistics
get rest pool           # thread status
```

---

## Message broker service (local)

Configures the AnyLog node itself as an MQTT broker so clients can publish directly to it.

```anylog
<run message broker where
  external_ip = [ip] and external_port = [port] and
  internal_ip = [local_ip] and internal_port = [local_port] and
  bind = [true/false] and threads = [count]>
```

Examples:
```anylog
run message broker where external_ip = !ip and external_port = !port and threads = 3

run message broker where external_ip = !external_ip and external_port = 7850 and internal_ip = !ip and internal_port = 7850 and threads = 6
```

Monitor:
```anylog
get local broker
```

---

## Message client (subscribe to external broker)

Subscribes to a third-party MQTT or REST broker and maps incoming data to database tables.

```anylog
<run msg client where
  broker = [url|local|rest] and port = [port] and
  user = [user] and password = [password] and log = [true/false] and
  topic = (
    name = [topic] and
    dbms = [dbms] and
    table = [table] and
    [column mapping]
  )>
```

> See [Data Ingestion — run msg client](/docs/data-ingestion/#run-msg-client) for full parameter reference and examples.

Monitor subscriptions:
```anylog
get msg clients
get msg client where id = 3
get msg client where broker = driver.cloudmqtt.com:18785 and topic = mydata
```

---

## Kafka consumer

```anylog
<run kafka consumer where
  ip = [ip] and port = [port] and
  reset = [latest|earliest] and
  topic = (
    name = [topic] and
    dbms = [dbms] and
    table = [table] and
    [column mapping]
  )>
```

- `reset` — `latest` (default) or `earliest` — determines the starting offset

Example:
```anylog
<run kafka consumer where
  ip = 198.74.50.131 and port = 9092 and
  reset = earliest and
  topic = (
    name = sensor and
    dbms = lsl_demo and
    table = ping_sensor and
    column.timestamp.timestamp = "bring [timestamp]" and
    column.value.int = "bring [value]"
  )>
```

Monitor with `get msg clients` (same as MQTT).

---

## gRPC client

Subscribes to a gRPC service (e.g. KubeArmor) and maps data using a mapping policy.

```anylog
run grpc client where name = [name] and ip = [ip] and port = [port] and policy = [policy id]
```

Example:
```anylog
run grpc client where name = kubearmor and ip = 127.0.0.1 and port = 32767 and policy = deff520f1096bcd054b22b50458a5d1c
```

Monitor:
```anylog
get grpc client
```

---

## SMTP client

Enables email notifications from scheduled tasks or the rule engine.

```anylog
<run smtp client where
  host = [host] and port = [port] and
  email = [address] and password = [password] and
  ssl = [true/false]>
```

Example:
```anylog
run smtp client where email = anylog.iot@gmail.com and password = mypassword
```

---

## Scheduler

Users can define multiple schedulers, each containing tasks that run periodically.

```anylog
run scheduler [id]    # id defaults to 1 (user scheduler); 0 is the system scheduler
```

Monitor:
```anylog
get scheduler
get scheduler 1
```

---

## Streamer

Required when using **streaming mode** for data ingestion. Enforces time-based buffer flush thresholds.

```anylog
run streamer
```

Check streaming buffer status:
```anylog
get streaming
```

---

## Blobs archiver

Manages large object (blob) storage on the node.

```anylog
<run blobs archiver where
  blobs_dir = [data dir] and archive_dir = [archive dir] and
  dbms = [true/false] and file = [true/false] and compress = [true/false]>
```

Example:
```anylog
run blobs archiver where dbms = true and file = true and compress = false
```

Monitor:
```anylog
get blobs archiver
```
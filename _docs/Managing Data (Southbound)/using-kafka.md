---
title: Kafka
description: How to publish and receive content from Kafka into AnyLog 
layout: page
---

<!--
## Changelog
- 2026-04-17 | Created document
- 2026-04-22 | Massimiliano review 
--> 

## Overview

Nodes in the AnyLog Network interact with Kafka in 2 ways:
* AnyLog serves as a Data Producer to Kafka - any result set of a query can be directed to a Kafka instance.   
* AnyLog is a Data Consumer - Kafka serves as a [message broker](message%20broker.md#using-a-message-broker) that transfers data to the network nodes.  
  
## Prerequisites

* An AnyLog Network with nodes hosting data.
* A configured Kafka instance.

## AnyLog serves as a Data Producer 

A query issued to the network can direct the result set to a Kafka instance.  
The Kafka instance is identified by an IP and port, and the query result set is associated with a topic.  

The following command, issued on the AnyLog CLI, sends 10 row from a table managed by nodes in the network to a Kafka instance:

```anylog
run client () sql litsanleandro format = json:output and stat  = false and dest = kafka@198.74.50.131:9092 and topic = ping_data "select device_name, timestamp, value, from ping_sensor where timestamp > now() - 1 day limit 10"
```

Note:
* The format directive _json:output_ organizes each set of timestamp and value (that are returned by the query) in JSON.
* The destination is identified by the key _Kafka_ followed by the Kafka configured IP and Port (dest = kafka@198.74.50.131:9092).
* The Kafka topic that is associated with the data in the example above is `ping_data`

## AnyLog serves as a Data Consumer

Each node in the AnyLog Network can be configured as a data consumer.  
The flow of data from a Kafka instance to the network is detailed in [The Southbound Connectors Diagram](adding%20data.md#the-southbound-connectors-diagram).

The command `run kafka consumer` initiates a process that serves as a client that subscribes to one or more topics 
and consume published messages by pulling data from the Kafka instance.

**Usage**:

```anylog
run kafka consumer where ip = [ip] and port = [port] and reset = [latest/earliest] and topic = [topic and mapping instructions]
```

**Command options**:

| Key        | Value  | Default  |
| ---------- | -------| ------- |
| ip         | The Kafka broker IP. |  |
| Port       | The Kafka broker port. | |
| reset      | Determines the offset policy. Optional values are _latest_ or _earliest_| _latest_ |
| topic      | One or more topics with mapping instructions.| |

Details on the topic declaration and mapping instructions are available [here](message%20broker.md#the-topic-params).  

**Example**:

```anylog
run kafka consumer where ip = 198.74.50.131 and port = 9092 and reset = latest and topic = (name = ping_data and dbms = lsl_demo and table = ping_sensor and column.timestamp.timestamp = "bring [timestamp]" and column.value.int = "bring [value]")
```

### Using local Kafka for development

Use this flow when you need a **local** Kafka broker for tests (for example mapping `run kafka consumer` to a topic).

1. Run a Kafka container

```bash
docker run -d --rm --name kafka-dev -p 9092:9092 apache/kafka:latest
```

2. Check logs

```bash
docker logs -f kafka-dev
```

3. Stop / remove

```bash
docker stop kafka-dev
docker rm -f kafka-dev
```

*(If you used `--rm` on `docker run`, the container is removed when it stops; `docker rm -f` is only needed if the name is still reserved.)*

4. Create topic `test`

Use **`localhost:9092`** for `--bootstrap-server` when the Kafka CLI runs **inside** the `kafka-dev` container (`docker exec` on the machine where that container runs). If you run the same kind of command **from another host on the LAN** and reach the broker over the network, use the **broker machine’s LAN IP and port** instead — for example **`192.168.1.101:9092`** (replace with the real address where port `9092` is published).

**On the Kafka host (inside the container):** use **`localhost`** or a **LAN IP** (for example **`192.168.1.101`**) for **`--bootstrap-server`**, depending on how the CLI reaches the broker from this shell.

```bash
docker exec kafka-dev /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --if-not-exists \
  --topic test --partitions 1 --replication-factor 1
```

5. Send a message to topic `test`

Example payload:

```json
{
  "timestamp": 1776294106000,
  "value": 42.0,
  "deviceID": "d1"
}
```

Publish one line (JSON) to the topic. Same **`--bootstrap-server`** rule as step **4** (`localhost` or LAN IP).

**On the Kafka host (inside the container):** use **`localhost`** or a **LAN IP** (for example **`192.168.1.101`**) for **`--bootstrap-server`**.

```bash
echo '{"timestamp":1776294106000,"value":42.0,"deviceID":"d1"}' | \
docker exec -i kafka-dev /opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic test
```

6. Verify messages (read from beginning)

Use a **new** consumer group and `auto.offset.reset=earliest` so you do not inherit an old committed offset. Again: **`localhost`** inside `docker exec`, or **`192.168.1.101`** from another LAN client.

**On the Kafka host (inside the container):** use **`localhost`** or a **LAN IP** (for example **`192.168.1.101`**) for **`--bootstrap-server`**.

```bash
docker exec kafka-dev /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic test \
  --group "tmp-$(date +%s)" \
  --consumer-property auto.offset.reset=earliest \
  --max-messages 5
```

7. Prepare Kafka consumer in AnyLog with one destination table only

Issue **`run kafka consumer`** on an **operator** node: the node that runs the **operator** process and hosts the destination **`dbms`** / table where Kafka rows are written.

On the AnyLog CLI, connect the logical DBMS, set **`broker_ip`** once, then start **`run kafka consumer`** so every message on topic **`test`** maps into **one** table (`kafka_demo` in this example — use any single table name **created in the `new_company` database**).

```anylog
connect dbms new_company where type = sqlite
```

```anylog
broker_ip = localhost
```

Broker on another machine on the LAN (that host’s address):

```anylog
broker_ip = 192.168.1.101
```

Use **`localhost`** when the AnyLog node and the Kafka broker listen on the **same** machine; use a **LAN IP** (for example **`192.168.1.101`**) when the broker runs elsewhere and the node reaches it over the network.

One topic → one table (adjust **`column.*`** to match your JSON keys):

```anylog
<run kafka consumer where ip = !broker_ip
    and port = 9092 and
    reset = earliest and
    topic = (name = test and
        dbms = new_company and
        table = kafka_demo and
        column.timestamp.timestamp = "bring [timestamp]" and
        column.value.float = "bring [value]" and
        column.deviceid.str = "bring [deviceID]")
>
```

8. Check configuration mapping

On the operator CLI (e.g. **`AL op1 >`**), confirm the Kafka subscription and how each topic maps to **`dbms`**, **`table`**, and **`column.*`**:

```anylog
get msg client
```

Example output:

```text
Subscription ID: 0001
User:         unused
Broker:       192.168.1.88:9092
Connection:   Kafka Consumer

     Messages    Success     Errors      Last message time    Last error time      Last Error
     ----------  ----------  ----------  -------------------  -------------------  ----------------------------------
             16          16           0  2026-04-21 09:01:19

     Subscribed Topics:
     Topic Dynamic QOS DBMS        Table      Column name Column Type Mapping Function Optional Policies
     -----|-------|---|-----------|----------|-----------|-----------|----------------|--------|--------|
     test |False  |  0|new_company|kafka_demo|timestamp  |timestamp  |['[timestamp]'] |False   |        |
          |False  |   |           |          |value      |float      |['[value]']     |False   |        |
          |False  |   |           |          |deviceid   |str        |['[deviceID]']  |False   |        |
```

#### Send new messages

From the host, pipe JSON into the Kafka producer (use your running container name or ID from `docker ps`, e.g. **`kafka-dev`**):

```bash
echo '{"timestamp":1776294106000,"value":23.1,"deviceID":"d1"}' | \
docker exec -i kafka-dev /opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic test
```

#### Verify data are being received

On the operator AnyLog CLI (example prompt **`AL op1 >`**), check streaming counters for the destination table:

```anylog
get streaming
```

Example output (non-zero **Streaming Rows** / **Calls** shows traffic is reaching the mapped `dbms` / table):

```text
Statistics
                       Put    Put     Streaming Streaming Cached Counter    Threshold   Buffer   Threshold  Time Left Last Process 
DBMS-Table             files  Rows    Calls     Rows      Rows   Immediate  Volume(KB)  Fill(%)  Time(sec)  (Sec)     HH:MM:SS     
----------------------|------|-----|-|---------|---------|------|----------|-----------|--------|----------|---------|------------|
new_company.kafka_demo|     0|    0| |       16|       16|     0|         0|         10|     0.0|        10|       10|00:01:41    |
```

#### Read data

Query the destination table on the same node:

```anylog
sql new_company "select * from kafka_demo"
```

Example result (trimmed):

```json
{
  "Query": [
    {
      "row_id": 1,
      "insert_timestamp": "2026-04-21 08:11:25.065903",
      "tsd_name": "251",
      "tsd_id": 61349,
      "timestamp": "2026-04-15 23:01:46.000000",
      "value": 22.0,
      "deviceid": "d1"
    },
    {
      "row_id": 2,
      "insert_timestamp": "2026-04-21 08:12:05.120608",
      "tsd_name": "251",
      "tsd_id": 61351,
      "timestamp": "2026-04-15 23:01:46.000000",
      "value": 12.0,
      "deviceid": "d1"
    },
    {
      "row_id": 3,
      "insert_timestamp": "2026-04-21 08:26:15.406653",
      "tsd_name": "251",
      "tsd_id": 61353,
      "timestamp": "2026-04-15 23:01:46.000000",
      "value": 23.1,
      "deviceid": "d1"
    }
  ],
  "Statistics": [{ "Count": 3, "Time": "00:00:00", "Nodes": 1 }]
}
```

### Use dynamic table creation

This flow creates **one physical table per `deviceID`** by using a **`bring`** expression for **`table`** in **`run kafka consumer`** (for example `kafka_stream_d1`, `kafka_stream_d2`). Run it on an **operator** node that can reach the broker and owns **`new_company`**.

#### 1) Create topic `stream1`

On the Kafka host (same pattern as topic **`test`**; use **`localhost`** or your broker address for **`--bootstrap-server`**):

```bash
docker exec kafka-dev /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --if-not-exists \
  --topic stream1 \
  --partitions 1 \
  --replication-factor 1
```

#### Map topic `stream1` to dynamic table names from `deviceID`

Subscribe so each row’s **`deviceID`** becomes part of the table name (prefix **`kafka_stream_`** + value of **`deviceID`**):

```anylog
<run kafka consumer where ip = 192.168.1.88 and
    port = 9092 and
    topic = (name = stream1 and
        dbms = new_company and
        table = "bring kafka_stream _ [deviceID]" and
        column.timestamp.timestamp = "bring [timestamp]" and
        column.value.float = "bring [value]" and
        column.deviceid.str = "bring [deviceID]")
>
```

Replace **`192.168.1.88`** with your broker IP (or use **`ip = !broker_ip`** if you set **`broker_ip`** earlier). Confirm mapping on the operator CLI:

```anylog
get msg client
```

Example output (note **Dynamic** table expression and resolved table pattern):

```text
Subscription ID: 0007
User:         unused
Broker:       192.168.1.88:9092
Connection:   Kafka Consumer

     Messages    Success     Errors      Last message time    Last error time      Last Error
     ----------  ----------  ----------  -------------------  -------------------  ----------------------------------
              2           2           0  2026-04-21 10:43:28

     Subscribed Topics:
     Topic   Dynamic QOS DBMS        Table                               Column name Column Type Mapping Function Optional Policies
     -------|-------|---|-----------|-----------------------------------|-----------|-----------|----------------|--------|--------|
     stream1|False  |  0|new_company|['kafka_stream', '_', '[deviceID]']|timestamp  |timestamp  |['[timestamp]'] |False   |        |
            |False  |   |           |                                   |value      |float      |['[value]']     |False   |        |
            |False  |   |           |                                   |deviceid   |str        |['[deviceID]']  |False   |        |
```

#### 3) Send sample rows with different `deviceID` values

```bash
echo '{"timestamp":1776294108000,"value":24.43,"deviceID":"d1"}' | \
docker exec -i kafka-dev /opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic stream1

echo '{"timestamp":1776294106000,"value":21.19,"deviceID":"d2"}' | \
docker exec -i kafka-dev /opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic stream1
```

#### 4) Verify streaming and per-device tables

```anylog
get streaming
```

Example output (one row count per dynamic table):

```text
Statistics
                                Put    Put     Streaming Streaming Cached Counter    Threshold   Buffer   Threshold  Time Left Last Process
DBMS-Table                      files  Rows    Calls     Rows      Rows   Immediate  Volume(KB)  Fill(%)  Time(sec)  (Sec)     HH:MM:SS
-------------------------------|------|-----|-|---------|---------|------|----------|-----------|--------|----------|---------|------------|

new_company.kafka_stream_d1    |     0|    0| |        1|        1|     0|         0|         10|     0.0|        10|       10|00:00:14    |
new_company.kafka_stream_d2    |     0|    0| |        1|        1|     1|         0|         10|     0.7|        10|        3|00:00:07    |
```

Read each table:

```anylog
sql new_company "select * from kafka_stream_d1"
```

```json
{
  "Query": [
    {
      "row_id": 1,
      "insert_timestamp": "2026-04-21 10:43:38.580379",
      "tsd_name": "251",
      "tsd_id": 63666,
      "timestamp": "2026-04-15 23:01:48.000000",
      "value": 24.43,
      "deviceid": "d1"
    }
  ],
  "Statistics": [{ "Count": 1, "Time": "00:00:00", "Nodes": 1 }]
}
```

```anylog
sql new_company "select * from kafka_stream_d2"
```

```json
{
  "Query": [
    {
      "row_id": 1,
      "insert_timestamp": "2026-04-21 10:43:48.678498",
      "tsd_name": "251",
      "tsd_id": 63667,
      "timestamp": "2026-04-15 23:01:46.000000",
      "value": 21.19,
      "deviceid": "d2"
    }
  ],
  "Statistics": [{ "Count": 1, "Time": "00:00:00", "Nodes": 1 }]
}
```

### Related commands

| Command                                                          | Info provided  |
|------------------------------------------------------------------| -------|
| [get processes](monitoring%20nodes.md#the-get-processes-command) | Background processes to determine if Kafka is enabled |
| [get msg client](monitoring%20calls.md#get-msg-clients)          | Subscriptions to brokers to determine related configurations and data consumed from Kafka instances |
| [get streaming](monitoring%20calls.md#get-streaming)             | Data consumed from brokers associated to dbms tables |
| [get operator](monitoring%20calls.md#get-operator)               | Statistics on ingestion of data to database tables |


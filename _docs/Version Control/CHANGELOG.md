---
title: Changelog
description: Release history and notable changes across all AnyLog Network versions.
layout: page
---

## Unreleased
<!-- Developers: add bullets below as changes land in your branch -->

### April 2026 (post 1.4.2603)

#### ✨ New Features
- **Python package inspection tool**: outputs installed packages in table or JSON format, with optional filtering by package name
- **MCP proxy layer**: routes and forwards MCP requests between nodes

#### 🐛 Bug Fixes
- Fixed MCP server tool descriptions for query and UNS operations
- Fixed POST routing bug in MCP proxy
- Fixed Grafana integration errors
- Fixed MQTT broker connection and message handling issues
- Fixed UNS pull info retrieval (`get_pull_info`)
- Fixed JSON POST message formatting
- Fixed string concatenation errors affecting query processing
- Fixed DBMS processing time calculation
- Fixed bug in reading scripts from policies
- Fixed `chown` location issue in Docker container startup
- Fixed PostgreSQL — stopped generating CSV output during `run immediate` commands
- Fixed blockchain bug in `pprint` output formatting
- Fixed messages to client formatting

#### 🔧 Improvements
- Dockerfile now displays `anylog@[node-name]-[hostname]` on `exec`, making it immediately clear when inside a container
- Cross-platform config switching: configs now cleanly toggle between Linux and Windows
- Removed redundant `chown` calls to streamline container initialization
- Reorganized `deploy_anylog` structure for cleaner builds
- Updated path resolution logic for more reliable cross-environment deployment
- Node scripts updated for consistency
- Set `User-Agent` header to `AnyLog-Agent` for consistent API identification
- TAG comments added for improved version tracking clarity
- Nicer CLI output formatting

#### ⚙️ Infrastructure & DevOps
- Workflow permission fixes and branch automation improvements
- Image builder updated to support Unix in addition to Linux
- Docker package hidden imports consolidated
- `setup.cfg` updated for packaging configuration

---

## 1.4.2603 (pre-develop · 8a98ca · 2026-03-16)

### ✨ New Features
- **REST API via message body**: AnyLog commands can now be sent via REST calls embedded in the HTTP message body without requiring custom headers — broadens client compatibility
- **MCP Server — AnyLog Command Relay**: MCP server can now reply with native AnyLog commands and handle POST requests, enabling richer AI-agent ↔ node interaction
- **REST `/api/status` endpoint**: New status call exposed via the REST interface
- **gRPC support for AI video inference**: Nodes can now receive and process AI inference results over gRPC streams, enabling real-time video analytics pipelines
- **Automated MQTT client**: MQTT client can now be configured and launched automatically from node policy, reducing manual setup steps
- **Multi-threaded MQTT client**: MQTT message ingestion now runs across a pool of threads, significantly improving throughput for high-volume message streams
- **MQTT message logging**: Incoming MQTT data is now logged for auditability and debugging
- **Aggregations in UNS and MCP**: Time-series aggregation functions are now available within both the Unified Namespace and MCP interfaces
- **PCAP data ingestion**: Added support for ingesting and processing PCAP (network packet capture) data
- **Semantic UNS policies**: UNS policies updated to support semantic Unified Namespace structure, including `source_node` tracking
- **TCP thread management**: Added configurable thread counts for TCP, REST, and Broker services; threads can now be gracefully terminated
- **Blockchain — get root policies**: New command to retrieve root-level blockchain policies
- **Policy indexing**: Indexes added to policy lookups for faster blockchain queries
- **MCP — get data nodes**: New MCP call to enumerate available data nodes in the network
- **MCP — `getChildPolicies`**: New MCP method to retrieve child policies from a parent policy context
- **UNS moved to Enterprise tier**: Unified Namespace functionality migrated to the enterprise version of AnyLog
- **Cluster policy excluded from namespace**: Cluster policies are no longer included in the UNS namespace to prevent conflicts
- **Node-RED flow updated**: Node-RED integration configuration updated to reflect current node architecture
- **Deployment script selection**: Node deployment now supports selecting from multiple deployment scripts at launch

### 🐛 Bug Fixes
- Fixed SQL parsing error with `AVG` aggregate queries
- Fixed MCP server — redundant trailing comma in generated responses
- Fixed MCP for Ollama integration — corrected API call format
- Fixed `blockchain get (operator,) bring.first` query returning incorrect results
- Fixed video plugin import errors
- Fixed aggregation edge cases in OPC-UA data flows
- Fixed `drop dbms` command bug
- Fixed queries using `include` directive returning wrong results
- Fixed JSON file reading in relational query context
- Fixed MQTT not starting correctly in PoC environments
- Fixed table names auto-generated from MQTT broker — now correctly forced to lowercase
- Fixed error in policy validation logic
- Fixed null handling in JSON-to-SQL mapping transformations
- Fixed null handling in general JSON processing
- Fixed uninitialized variable in message handling
- Fixed data type coercion between `int` and `date` types
- Fixed MQTT log write errors
- Fixed `str_to_list` transformation used in `bring` command mapping
- Fixed mapping policy bug with `__start__` / `__end__` script delimiters
- Fixed certificate handling in TLS/SSL connections
- Fixed SQL INSERT missing `NULL` values in generated statements
- Fixed aggregations crash when encountering `None` values
- Fixed aggregations value mismatch (reported externally)
- Fixed error message for malformed row structures
- Fixed quotation issue with license key handling

### 🔧 Improvements
- Exception handling improved: `logger` calls replaced with proper `exception` handlers for better error traceability
- `anylog docker build` updated for Python 3.13 compatibility
- gRPC client updated with crash guards and improved inline documentation
- `blockchain get` simplified — operator reads no longer require full policy fetch
- `bring.json` output — single quotes now correctly replaced with double quotes
- MCP server relays replies directly to the dashboard with `Connection` keep-alive headers
- Video streaming: added connection retry support and utility for writing JSON lists to file
- MCP thread count is now configurable and capped to prevent resource exhaustion
- Force-install flag added to requirements installation to prevent version conflicts
- `if/else` logic added for blockchain conditional policy evaluation
- Mapping policy naming convention standardized
- Workflow now supports version management automation
- Updated README with setup and usage documentation
- Proxy example added for MCP configuration reference

### ⚙️ Infrastructure & DevOps
- Docker builder updated and stabilized for multi-platform builds
- Docker home directory path resolution improved
- Docker paths corrected across environments
- Added `.gitignore` entries for log files and `__pycache__`
- `setup.cfg` updated for packaging metadata
- Synced `os-dev`, `ms-dev`, and `rs-dev` branches

---

## 2025 — Year in Review

The primary focus of 2025 was **edge deployment, containerization, and media integration**. Docker and Podman support was significantly expanded, with Makefile-driven build automation replacing manual image workflows. OPC-UA connectivity matured with improved async handling, and a new EtherIP protocol integration was added for industrial PLC communication. Video and camera pipeline support was introduced, enabling nodes to ingest and process media streams. Nebula-based overlay networking was stabilized for secure node-to-node communication. The aggregations engine was substantially extended. Akave decentralized storage was integrated as a new data sink, and remote deployment templates were improved to simplify multi-node rollouts.

---

## 2024 — Year in Review

2024 centered on **integrations, enterprise features, and observability**. Grafana dashboards were significantly improved with new query panels and data source configurations. OPC-UA support was introduced as a first-class data ingestion path. Async message processing was added to reduce latency on high-throughput nodes. The Nebula secure networking layer was introduced for overlay network management. License enforcement was tightened for enterprise deployments. The EdgeLake project emerged as a related effort, and mapping and transform rules were extended to handle more complex JSON-to-SQL conversion scenarios.

---

## 2023 — Year in Review

2023 was dominated by **packaging, licensing, and operational stability**. The policy system was heavily refined, with improved validation, child policy traversal, and namespace management. Docker images were rebuilt on Alpine Linux to reduce footprint, and a compiled binary distribution was introduced alongside the source distribution. License management was formalized with enforcement hooks in the node startup sequence. Syslog ingestion was added as a native data source. Configuration management was streamlined, and a significant body of work went into improving error messages and CLI output for both developers and operators.

---

## 2022 — Year in Review

2022 focused on **deployment maturity, remote operations, and data management**. Docker volume management was overhauled to support persistent and configurable storage layouts. Remote node deployment — including over Grafana and REST — was a major theme, enabling operators to manage distributed nodes without direct shell access. Blob storage support was introduced for handling unstructured data alongside time-series. PostgreSQL was established as a production-grade backend alongside SQLite. Mapping policies were introduced to declaratively transform incoming data, and the operator/publisher model was refined for multi-node topologies.

---

## 2021 — Year in Review

2021 introduced **Ethereum blockchain integration and streaming data support**. Nodes could now anchor metadata and policy records to Ethereum, providing an immutable audit trail alongside the native AnyLog blockchain. Streaming ingestion was added as a complement to batch and REST-based data ingest. Authentication flows were improved with more robust session and token handling. Timezone-aware query processing was added, fixing a class of timestamp inconsistencies in distributed queries. Docker-based deployment was formalized and monitoring and alerting hooks were extended.

---

## 2020 — Year in Review

2020 was the year of **platform expansion and enterprise readiness**. The query engine was significantly extended with OLEDB connection support, enabling BI tools to query AnyLog nodes directly. Grafana integration was introduced as the primary visualization layer. An authentication framework was built to secure REST and TCP interfaces. Partition-based data management was added for time-series tables, improving query performance on large datasets. The operator, publisher, and consumer node roles were formalized into a coherent distributed processing model. SQLite was hardened as the default embedded database.

---

## 2019 — Year in Review

2019 was the **core platform build-out year**. The AnyLog query interface was designed and implemented, establishing the SQL-like command language that underpins all data access. The blockchain layer was introduced for decentralized policy and metadata management. A messaging and script system was built to allow nodes to exchange commands and execute policy-driven workflows. The client-server architecture was stabilized, and an extensive suite of integration tests was developed. Debugging infrastructure and trace logging were added to support early adopters.

---

## 2018 — Year in Review

The AnyLog Network project was founded in mid-2018. Initial commits established the core concepts: **producer nodes** that generate and publish sensor data, **contractor nodes** that receive and store it, and a lightweight **query layer** for retrieving records. Early work included sensor data generators producing JSON and SQL output, pseudo-code for the producer/contractor protocol, and foundational README documentation. The repository structure, GitHub configuration, and initial branching strategy were all put in place during this period.

---

*For the full commit-level history, run `git log` or browse the repository on GitHub.*
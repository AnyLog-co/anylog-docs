---
title: Telegraf
description: How to utilize Telegraf with generic mapping policies 
layout: page
Changelog: 
    * 2026-04-17 created document 
---

# Telegraf

<a href="https://www.influxdata.com/time-series-platform/telegraf/" target="_blank">Telegraf</a> is _InfluxData_'s tool to
connect between southbound services (ex. system logs) and the storage layer. 

In order to utilize it for AnyLog, the recommend northbound inputs are MQTT or REST POST.

## What is a mapping policy 

Publishing data into AnyLog via (REST) POST or MQTT allows the user to correlate the JSON content with the database
table and column names to be used - ie mapping. 

AnyLog maps incoming JSON data to relational tables using mapping policies — JSON structures stored in the shared 
metadata layer. Each policy defines the source-to-destination transformation, specifying the target database, table, 
and schema.

Source data arrives in one of two shapes: flat key-value pairs (e.g., London Air Quality data), or a list of 
dictionaries where each entry is a reading. The core extraction mechanism is the _bring_ command, which pulls values 
from the source JSON and optionally transforms them. Mapping policies can be linked to data either directly via the run 
mqtt client command or by referencing a stored policy by ID.

This can be done in a hardcoded fashion or relative referencing. 

### Hardcoded Mapping 

A mapping policy has the following top-level keys:

| Key | Required | Purpose | 
|:---:| :---: | :---: | 
| id  | Yes | Unique policy identifier | 
| dbms | Yes | Target logical database | 
| table | Yes | Target table name | 
| readings | Yes - but could be empty | Key pointing to a list of readings in the source JSON | 
| condition | No | if statement to conditionally apply the policy  | 
| schema | Yes | Column definitions and mapping instructions | 
    

Each column in the schema is a dictionary with a bring expression (to extract the value), a type (string, integer, 
float, timestamp, bool, varchar, char), an optional condition, and an optional default fallback.

For blob data (images, video), additional keys like blob, extension, apply (e.g. base64 decoding), and hash extend the 
schema to route large objects to a dedicated object store while keeping a reference ID in the relational table.


#### Example

Lets take the example from [southbound overview](southound-overview.md#knowing-your-topics-and-schemas)

```anylog
<run msg client where
  broker = mqtt.mycompany.com and port = 1883 and
  topic = (
    name = sensors and
    dbms = my_data and
    table = temperature_readings and
    column.timestamp.timestamp = "bring [timestamp]" and
    column.device_name.str = "bring [device]" and
    column.value.float = "bring [temperature]"
  )>
```

A correlating alternative would be to use a mapping policy
```anylog
{
    "mapping": {
        "id": "sensors",
        "dbms": "my_data",
        "table": "temperature_readings",
        "readings": "", 
        "schema": {
            "timestamp": {
                "type": "timestamp", 
                "default": "now()",
                "bring": "[timestamp]"
            },
            "device_name": {
                "type": "string", 
                "default": "",
                "bring": ["device]"
            },
            "value": {
                "type": "float", 
                "default": null,
                "bring": "[value]"
            }
        }
    }
}
```

```
<run msg client where
  broker = mqtt.mycompany.com and port = 1883 and
  topic = (
    name = sensors and 
    policy = sensors
  )>    
```


### Regular versus generic Mapping Policy 

## Setting up Telegraf 

## Getting from Telegraf into AnyLog



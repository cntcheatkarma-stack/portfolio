# Weather Station Mesh Node

**Status:** Planning
**Category:** Hardware, IoT, local AI

## Summary

A weather station mounted on a roof or pole that doubles as a mesh network node. It reports readings from several environmental sensors to an indoor base station, where a locally hosted language model lets me ask about the data in plain English (for example, "What was the peak wind speed today?").

## Planned architecture

```
[Outdoor node: sensors + LoRa mesh radio]
        |  LoRa mesh (Meshtastic)
        v
[Indoor node] --USB/serial--> [Python service] <--> [Local LLM (tool calling)]
```

- **Outdoor node:** sensors connected to a LoRa board running Meshtastic firmware
- **Indoor node:** receives sensor packets over the mesh
- **Python service:** stores readings and exposes them as tools the local model can call
- **Local model:** turns a natural-language question into a tool call and answers from the real data. It doesn't make up readings.

## Candidate sensors

| Measurement | Candidate parts |
|---|---|
| Temperature / humidity / pressure | BME280, SHT31 |
| Wind and rain | Ecowitt WS85 |
| Battery / solar monitoring | INA219 |

## Open questions

- [ ] Final list of measurements (UV, air quality, etc.)
- [ ] Whether to join the public Meshtastic mesh or use a private channel
- [ ] Power budget and solar sizing
- [ ] Weatherproof enclosure and mounting

## Security considerations

- A private mesh channel with its own encryption key keeps the sensor data off the public mesh.
- The local model should only *read* sensor data. No tool it can call should change node settings.
- Running the model locally keeps all the data on my own network.

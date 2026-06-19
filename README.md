# pyfarm-iot

Hardware drivers for PyFarm edge devices — the layer that turns GPIO pins, I²C
buses and MQTT topics into the `Sensor` and `Actuator` contracts the control
engine speaks.

## What's here

This package implements the contracts defined in `pyfarm-core`
(`pyfarm.core.sensor.Sensor`, `pyfarm.core.actuator.Actuator`) for real
hardware:

- **Sensors:** DHT22 temperature/humidity, ADC-backed analog (e.g. MCP3008 for
  CO₂), and replay/fake variants for bench testing.
- **Actuators:** GPIO relays, PWM outputs (fans/dimmers), and MQTT devices
  (Tasmota/ESPHome/Home Assistant).

> **Status — Phase 0:** scaffolding only. The concrete drivers currently live in
> `pyfarm-control` (`pyfarm.control.sensors` / `pyfarm.control.actuators`). They
> will migrate here once the core contracts are stable; for now this package
> re-exports the base contracts so the import location is settled. See
> `pyfarm-control/EXTENSIONS.md` for the driver design.

## Install

```bash
pip install pyfarm-iot                 # contracts only (any machine)
pip install 'pyfarm-iot[hardware]'     # + RPi.GPIO / adafruit backends (on a Pi)
```

Drivers import their hardware backends lazily, so importing `pyfarm.iot` never
requires the hardware libraries — only calling a driver's `read()`/`apply()` on
the device does.

## Development

```bash
pip install -e ".[dev]"
pytest
```

"""Hardware drivers for pyfarm edge devices."""

from __future__ import annotations

from pyfarm.iot.registry import register_actuator

# Import and register actuator drivers
from .actuators import MQTTActuator, PWMActuator, RelayActuator

# Register drivers via decorators
register_actuator("relay")(RelayActuator)
register_actuator("pwm")(PWMActuator)
register_actuator("mqtt")(MQTTActuator)

# Sensors currently not exposed via registry (can add later if needed)
from .sensors import ADCSensor, DHT22Sensor  # noqa: E402, F401

__all__ = [
    "DHT22Sensor",
    "ADCSensor",
    "RelayActuator",
    "PWMActuator",
    "MQTTActuator",
]

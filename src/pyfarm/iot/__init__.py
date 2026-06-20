"""pyfarm-iot: hardware drivers for PyFarm edge devices.

This package implements the sensor/actuator contracts defined in
:mod:`pyfarm.core.sensor` and :mod:`pyfarm.core.actuator` for real hardware
(GPIO relays, PWM, DHT22, ADC-backed analog sensors, MQTT devices).

Provides a pluggable driver registry so pyfarm-control can resolve spec
`kind` names to concrete hardware implementations.

Install the hardware backends with ``pip install 'pyfarm-iot[hardware]'`` on a
Raspberry Pi; the drivers lazily import their backends, so importing this
package is always safe on any machine.
"""

from __future__ import annotations

from pyfarm.core.actuator import Actuator, Command
from pyfarm.core.sensor import Sensor
from pyfarm.iot.registry import (
    build_actuator,
    register_actuator,
    register_sensor,
)

# Import drivers to trigger registration
from pyfarm.iot import drivers as _drivers  # noqa: F401

__all__ = [
    "Sensor",
    "Actuator",
    "Command",
    "build_actuator",
    "register_sensor",
    "register_actuator",
]

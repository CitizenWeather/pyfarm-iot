"""pyfarm-iot: hardware drivers for PyFarm edge devices.

This package implements the sensor/actuator contracts defined in
:mod:`pyfarm.core.sensor` and :mod:`pyfarm.core.actuator` for real hardware
(GPIO relays, PWM, DHT22, ADC-backed analog sensors, MQTT devices).

**Status (Phase 0):** scaffolding. The concrete drivers currently live in
``pyfarm-control`` (``pyfarm.control.sensors`` / ``pyfarm.control.actuators``);
they will migrate here in a later phase once the core contracts are stable. The
``Sensor`` and ``Actuator`` base classes are re-exported here so future drivers
(and downstream code) have a single import location.

Install the hardware backends with ``pip install 'pyfarm-iot[hardware]'`` on a
Raspberry Pi; the drivers lazily import their backends, so importing this
package is always safe on any machine.
"""

from __future__ import annotations

from pyfarm.core.actuator import Actuator, Command
from pyfarm.core.sensor import Sensor

__all__ = ["Sensor", "Actuator", "Command"]

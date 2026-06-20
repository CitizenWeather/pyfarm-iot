"""Importing pyfarm-iot must be safe on any machine (no hardware libs)."""

import pyfarm.iot
from pyfarm.core.actuator import Actuator
from pyfarm.core.sensor import Sensor


def test_reexports_core_contracts():
    assert pyfarm.iot.Sensor is Sensor
    assert pyfarm.iot.Actuator is Actuator

"""Hardware driver registry for pyfarm-iot.

Relocated from pyfarm-control to centralize hardware driver registration
and keep control's registry focused on notifications and orchestration.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Callable, TypeVar, Any

from pyfarm.core.actuator import Actuator
from pyfarm.core.sensor import Sensor

if TYPE_CHECKING:
    from pyfarm.control.spec.schema import ActuatorSpec

_SENSOR_REGISTRY: dict[str, type[Sensor]] = {}
_ACTUATOR_REGISTRY: dict[str, type[Actuator]] = {}

_S = TypeVar("_S", bound=type[Sensor])
_A = TypeVar("_A", bound=type[Actuator])


def register_sensor(kind: str) -> Callable[[_S], _S]:
    """Register a sensor class for a spec `kind` (e.g. 'dht22').

    Constructor: cls(sensor_id, metric, unit, **spec_fields)
    """

    def deco(cls: _S) -> _S:
        _SENSOR_REGISTRY[kind] = cls
        return cls

    return deco


def register_actuator(kind: str) -> Callable[[_A], _A]:
    """Register an actuator class for a spec `kind` (e.g. 'relay').

    Constructor: cls(name, spec) where spec is ActuatorSpec or dict-like.
    """

    def deco(cls: _A) -> _A:
        _ACTUATOR_REGISTRY[kind] = cls
        return cls

    return deco


def build_actuator(name: str, spec: Any) -> Actuator:
    """Build an actuator from spec, falling back to a stub on unknown kind.

    Args:
        name: Actuator name.
        spec: ActuatorSpec with a `kind` field.

    Returns:
        Actuator instance (hardware implementation or stub).
    """
    kind = getattr(spec, "kind", None)
    cls = _ACTUATOR_REGISTRY.get(kind)
    if cls is None:
        print(
            f"No actuator registered for kind '{kind}' — using stub for actuator '{name}'",
            file=sys.stderr,
        )
        return _StubActuator(name)
    return cls(name, spec)


class _StubActuator(Actuator):
    """Stub actuator that logs commands (used when hardware not available)."""

    def __init__(self, name: str, spec: Any = None):
        self.name = name

    async def on(self) -> None:
        print(f"[STUB] Turning on actuator {self.name}")

    async def off(self) -> None:
        print(f"[STUB] Turning off actuator {self.name}")

    async def get_state(self) -> dict:
        return {"state": "unknown"}

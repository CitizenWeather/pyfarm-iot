"""Hardware actuator implementations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pyfarm.core.actuator import Actuator, Command

if TYPE_CHECKING:
    from pyfarm.control.spec.schema import ActuatorSpec


class RelayActuator(Actuator):
    """GPIO relay actuator (on/off control).

    Lazily imports RPi.GPIO on first access.
    """

    def __init__(self, name: str, spec: Any):
        """Initialize GPIO relay actuator.

        Args:
            name: Actuator name/identifier.
            spec: ActuatorSpec with gpio field.
        """
        self.name = name
        self.spec = spec
        self.gpio_pin = getattr(spec, "gpio", None)
        self._initialized = False

    async def on(self) -> None:
        """Turn relay on (GPIO high)."""
        self._ensure_initialized()
        import RPi.GPIO as GPIO

        GPIO.output(self.gpio_pin, GPIO.HIGH)

    async def off(self) -> None:
        """Turn relay off (GPIO low)."""
        self._ensure_initialized()
        import RPi.GPIO as GPIO

        GPIO.output(self.gpio_pin, GPIO.LOW)

    async def get_state(self) -> dict:
        """Get relay state.

        Returns:
            {'state': 'on'|'off'}
        """
        self._ensure_initialized()
        import RPi.GPIO as GPIO

        state = GPIO.input(self.gpio_pin)
        return {"state": "on" if state else "off"}

    def _ensure_initialized(self) -> None:
        """Lazy GPIO setup on first access."""
        if self._initialized:
            return

        try:
            import RPi.GPIO as GPIO
        except ImportError as e:
            raise ImportError(
                "RPi.GPIO not installed. Install with: pip install 'pyfarm-iot[hardware]'"
            ) from e

        if self.gpio_pin is None:
            raise ValueError("gpio_pin required for RelayActuator hardware initialization")

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        self._initialized = True


class PWMActuator(Actuator):
    """PWM-controlled actuator (variable intensity).

    Lazily imports RPi.GPIO on first access.
    Supports intensity 0-100%.
    """

    def __init__(self, name: str, spec: Any):
        """Initialize PWM actuator.

        Args:
            name: Actuator name/identifier.
            spec: ActuatorSpec with gpio field.
        """
        self.name = name
        self.spec = spec
        self.gpio_pin = getattr(spec, "gpio", None)
        self.frequency = 50  # Default PWM frequency
        self._pwm = None
        self._initialized = False

    async def on(self) -> None:
        """Turn on at full intensity (100%)."""
        self._ensure_initialized()
        self._pwm.ChangeDutyCycle(100)

    async def off(self) -> None:
        """Turn off (0% intensity)."""
        self._ensure_initialized()
        self._pwm.ChangeDutyCycle(0)

    async def execute(self, command: Command) -> None:
        """Execute command to set intensity.

        Command format: intensity (0-100).
        """
        self._ensure_initialized()
        intensity = int(command.value) if hasattr(command, "value") else 50
        intensity = max(0, min(100, intensity))
        self._pwm.ChangeDutyCycle(intensity)

    async def get_state(self) -> dict:
        """Get PWM state.

        Returns:
            {'intensity': 0-100}
        """
        self._ensure_initialized()
        return {"intensity": self._pwm.value}

    def _ensure_initialized(self) -> None:
        """Lazy GPIO + PWM setup on first access."""
        if self._initialized:
            return

        try:
            import RPi.GPIO as GPIO
        except ImportError as e:
            raise ImportError(
                "RPi.GPIO not installed. Install with: pip install 'pyfarm-iot[hardware]'"
            ) from e

        if self.gpio_pin is None:
            raise ValueError("gpio_pin required for PWMActuator hardware initialization")

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self.gpio_pin, self.frequency)
        self._pwm.start(0)
        self._initialized = True


class MQTTActuator(Actuator):
    """MQTT-controlled actuator (remote IoT device).

    Targets Tasmota/ESPHome devices via MQTT broker.
    """

    def __init__(self, name: str, spec: Any):
        """Initialize MQTT actuator.

        Args:
            name: Actuator name/identifier.
            spec: ActuatorSpec with mqtt_topic field.
        """
        self.name = name
        self.spec = spec
        self.mqtt_topic = getattr(spec, "mqtt_topic", None)
        self.broker_url = "mqtt://localhost"
        self._client = None
        self._initialized = False

    async def on(self) -> None:
        """Send MQTT 'ON' command."""
        await self._ensure_connected()
        await self._publish("ON")

    async def off(self) -> None:
        """Send MQTT 'OFF' command."""
        await self._ensure_connected()
        await self._publish("OFF")

    async def execute(self, command: Command) -> None:
        """Execute MQTT command."""
        await self._ensure_connected()
        cmd = str(command.value) if hasattr(command, "value") else "ON"
        await self._publish(cmd)

    async def get_state(self) -> dict:
        """Get MQTT device state."""
        return {"status": "unknown"}  # Implement actual MQTT state query if needed

    async def _ensure_connected(self) -> None:
        """Lazy MQTT client initialization."""
        if self._initialized:
            return

        try:
            import asyncio_mqtt as aiomqtt
        except ImportError as e:
            raise ImportError(
                "asyncio_mqtt not installed. "
                "Install with: pip install 'pyfarm-iot[hardware]'"
            ) from e

        if self.mqtt_topic is None:
            raise ValueError("mqtt_topic required for MQTTActuator initialization")

        self._client = aiomqtt.Client(self.broker_url)
        await self._client.connect()
        self._initialized = True

    async def _publish(self, command: str) -> None:
        """Publish command to MQTT topic."""
        if self._client is None:
            raise RuntimeError("MQTT client not initialized")
        await self._client.publish(self.mqtt_topic, command)

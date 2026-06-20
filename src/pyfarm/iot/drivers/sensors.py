"""Hardware sensor implementations."""

from __future__ import annotations

from pyfarm.core.sensor import Sensor


class DHT22Sensor(Sensor):
    """DHT22 temperature/humidity sensor driver.

    Lazily imports adafruit-circuitpython-dht on first read.
    Pin/GPIO assignment is specified in the grow spec.
    """

    def __init__(
        self,
        sensor_id: str,
        metric: str = "temperature",
        unit: str = "celsius",
        gpio_pin: int | None = None,
    ):
        """Initialize DHT22 sensor.

        Args:
            sensor_id: Unique sensor identifier.
            metric: 'temperature' or 'humidity'.
            unit: 'celsius' or 'fahrenheit' for temperature; '%' for humidity.
            gpio_pin: GPIO pin number (BCM). Required for actual hardware.
        """
        self.sensor_id = sensor_id
        self.metric = metric
        self.unit = unit
        self.gpio_pin = gpio_pin
        self._device = None

    async def read(self) -> float:
        """Read temperature or humidity from DHT22.

        Returns:
            Temperature (°C or °F) or humidity (%) depending on metric.

        Raises:
            RuntimeError: If hardware not available or read fails.
        """
        if self._device is None:
            self._device = self._init_device()

        try:
            if self.metric == "temperature":
                return self._device.temperature
            elif self.metric == "humidity":
                return self._device.humidity
            else:
                raise ValueError(f"Unknown metric: {self.metric}")
        except Exception as e:
            raise RuntimeError(f"DHT22 read failed on pin {self.gpio_pin}: {e}")

    async def check_health(self) -> bool:
        """Check DHT22 sensor health (successful read within timeout)."""
        try:
            await self.read()
            return True
        except Exception:
            return False

    def _init_device(self):
        """Lazy import and initialize DHT22 device."""
        try:
            import board
            import adafruit_dht
        except ImportError as e:
            raise ImportError(
                "adafruit-circuitpython-dht not installed. "
                "Install with: pip install 'pyfarm-iot[hardware]'"
            ) from e

        if self.gpio_pin is None:
            raise ValueError("gpio_pin required for DHT22 hardware initialization")

        pin = getattr(board, f"D{self.gpio_pin}", None)
        if pin is None:
            raise ValueError(f"Board pin D{self.gpio_pin} not found")

        return adafruit_dht.DHT22(pin)


class ADCSensor(Sensor):
    """MCP3008-based analog-to-digital converter sensor.

    Reads analog sensors (CO₂, soil moisture, etc.) via SPI.
    Lazily imports Adafruit_MCP3008 on first read.
    """

    def __init__(
        self,
        sensor_id: str,
        metric: str = "analog",
        unit: str = "raw",
        channel: int = 0,
    ):
        """Initialize ADC sensor.

        Args:
            sensor_id: Unique sensor identifier.
            metric: Metric name (e.g., 'co2', 'soil_moisture').
            unit: Unit name (e.g., 'ppm', '%').
            channel: MCP3008 channel (0-7).
        """
        self.sensor_id = sensor_id
        self.metric = metric
        self.unit = unit
        self.channel = channel
        self._device = None

    async def read(self) -> float:
        """Read analog value from MCP3008 ADC.

        Returns:
            Raw ADC value (0-1023) or normalized (0.0-1.0) depending on configuration.

        Raises:
            RuntimeError: If hardware not available or read fails.
        """
        if self._device is None:
            self._device = self._init_device()

        try:
            return float(self._device.read_adc(self.channel))
        except Exception as e:
            raise RuntimeError(f"ADC read failed on channel {self.channel}: {e}")

    async def check_health(self) -> bool:
        """Check ADC sensor health (successful read within timeout)."""
        try:
            await self.read()
            return True
        except Exception:
            return False

    def _init_device(self):
        """Lazy import and initialize MCP3008 device."""
        try:
            import Adafruit_MCP3008
        except ImportError as e:
            raise ImportError(
                "Adafruit_MCP3008 not installed. "
                "Install with: pip install 'pyfarm-iot[hardware]'"
            ) from e

        return Adafruit_MCP3008.MCP3008()

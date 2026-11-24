"""
MicroPython Driver for ADS1115 16-Bit ADC
Optimized for ESP8266 multi-channel power monitoring
"""
import time

# Registers
_ADS1115_REG_POINTER_CONVERT = 0x00
_ADS1115_REG_POINTER_CONFIG  = 0x01

# PGA Full Scale voltage ranges
PGA_6_144V = 0x0000  # +/- 6.144V (LSB = 0.1875 mV) -> Ideal for 0-5V analog modules
PGA_4_096V = 0x0200  # +/- 4.096V (LSB = 0.1250 mV)
PGA_2_048V = 0x0400  # +/- 2.048V (LSB = 0.0625 mV)
PGA_1_024V = 0x0600  # +/- 1.024V (LSB = 0.03125 mV)

PGA_VOLTS = {
    PGA_6_144V: 6.144,
    PGA_4_096V: 4.096,
    PGA_2_048V: 2.048,
    PGA_1_024V: 1.024
}

# Single-ended MUX masks
_MUX_SINGLE = {
    0: 0x4000,  # AIN0 vs GND
    1: 0x5000,  # AIN1 vs GND
    2: 0x6000,  # AIN2 vs GND
    3: 0x7000   # AIN3 vs GND
}

class ADS1115:
    def __init__(self, i2c, address=0x48, pga=PGA_6_144V):
        self.i2c = i2c
        self.address = address
        self.pga = pga
        self.lsb_volts = PGA_VOLTS[pga] / 32768.0
        self._buf = bytearray(2)

    def _write_register(self, reg, val):
        self._buf[0] = (val >> 8) & 0xFF
        self._buf[1] = val & 0xFF
        self.i2c.writeto_mem(self.address, reg, self._buf)

    def _read_register(self, reg):
        self.i2c.readfrom_mem_into(self.address, reg, self._buf)
        val = (self._buf[0] << 8) | self._buf[1]
        if val >= 0x8000:
            val -= 0x10000
        return val

    def read_raw(self, channel):
        """Perform single-shot reading on channel 0, 1, 2, or 3."""
        if channel not in _MUX_SINGLE:
            raise ValueError("Channel must be 0, 1, 2, or 3")

        # Config: OS=1 (start conversion) | MUX | PGA | MODE=1 (single-shot) | DR=128SPS (0x0080) | COMP_QUE=disable (0x0003)
        config = 0x8000 | _MUX_SINGLE[channel] | self.pga | 0x0100 | 0x0080 | 0x0003
        self._write_register(_ADS1115_REG_POINTER_CONFIG, config)

        # Wait for conversion to finish (OS bit goes to 1 when done)
        for _ in range(50):
            time.sleep_ms(2)
            cfg = self._read_register(_ADS1115_REG_POINTER_CONFIG)
            if cfg & 0x8000:
                break

        # Read 16-bit signed conversion value
        raw = self._read_register(_ADS1115_REG_POINTER_CONVERT)
        return raw

    def read_voltage(self, channel, samples=5):
        """Read voltage with oversampling for high noise immunity."""
        total = 0.0
        valid_samples = 0
        for _ in range(samples):
            raw = self.read_raw(channel)
            volts = raw * self.lsb_volts
            if volts < 0.0:
                volts = 0.0
            total += volts
            valid_samples += 1
            time.sleep_ms(1)
        return total / valid_samples if valid_samples > 0 else 0.0

# Ammonia Demonstrator - Inlet Control System

A Modbus/RS485-based IoT control system for an ammonia synthesis demonstrator, using MQTT for communication.

## Architecture

```
main_inlet.py                    # Main orchestrator
    |
    +-- common_config.py         # Shared MQTT client & Modbus device factory
    |
    +-- sensor/read_HG803.py     # Temperature/humidity sensor (slave 3)
    +-- fan/fan_control.py       # Inlet fan controller (slave 4)
    +-- heater/relay_control.py  # Heater relay controller (slave 5)
    +-- pump/pump_control.py     # Peristaltic pump controller (slave 20)
    +-- hotend/PIDcontroller_control.py  # PID temperature controller (slave 25)
    +-- powermeter/read_powermeter.py    # Power meter reader (slave 60)
```

## Hardware Configuration

| Device | Slave Address | MQTT Topic |
|--------|---------------|------------|
| HG803 Sensor | 3 | `master/inlet/temperature`, `master/inlet/humidity` |
| Inlet Fan | 4 | `master/inlet/fan_in` |
| Heater Relay | 5 | `master/inlet/heater_relay` |
| Ammonia Pump | 20 | `master/inlet/ammonia_pump` |
| Hot-end PID | 25 | `master/inlet/hotend_temperature` |
| Powermeter | 60 | `slave/powerbox/total_import`, `slave/powerbox/total_export` |

## Dependencies

- `minimalmodbus` - Modbus RTU communication
- `paho-mqtt` - MQTT client
- `pyserial` - Serial port handling

---

# Code Review & Fixes (January 2026)

## Summary

A comprehensive code review was performed on `main_inlet.py` and all its dependencies. Issues were identified and fixed, organized by severity below.

---

## Critical Bugs Fixed

### 1. Shared MQTT Client Disconnect Problem

**Files:** `fan/fan_control.py`, `heater/relay_control.py`, `pump/pump_control.py`

**Problem:** Each device's cleanup method called `client.loop_stop()` and `client.disconnect()` on the shared MQTT client. Since `main_inlet.py` creates ONE shared client passed to all devices, the first device to stop would disconnect MQTT for ALL other devices.

```python
# BEFORE (bug) - fan_control.py
def fan_stop(self):
    ...
    self.client.loop_stop()    # Disconnects shared client!
    self.client.disconnect()
```

**Fix:** Removed MQTT disconnect from device classes. MQTT cleanup now happens once in `main_inlet.py` after all devices are stopped.

---

### 2. Type Annotation Used as Default Value

**File:** `powermeter/read_powermeter.py`

**Problem:** Function parameter used the class as a default value instead of a type hint.

```python
# BEFORE (bug)
def read_power(device = minimalmodbus.Instrument, client = None):

# AFTER (fixed)
def read_power(device: minimalmodbus.Instrument, client=None):
```

---

### 3. Missing None Checks in PID Controller

**File:** `hotend/PIDcontroller_control.py`

**Problem:** `controller_setup()` would write `None` to registers if parameters weren't provided.

**Fix:** Added validation to raise `ValueError` if any required parameter is missing.

```python
def controller_setup(device, SV=None, K_p=None, K_i=None, K_d=None, T=None, AR=None):
    if any(param is None for param in [SV, K_p, K_i, K_d, T, AR]):
        raise ValueError("All PID parameters must be provided")
    ...
```

---

## Reliability Improvements

### 4. Debug Mode in Production

**File:** `heater/relay_control.py`

**Issue:** `minimalmodbus.DEBUG = True` was left enabled, printing verbose output for every Modbus transaction.

**Status:** Left for user to remove manually (user preference).

---

### 5. Input Validation on MQTT Messages

**Files:** `fan/fan_control.py`, `pump/pump_control.py`

**Problem:** No bounds checking on incoming MQTT values. Invalid values (e.g., `9999` or `-100`) would be sent directly to hardware.

**Fix:** Added validation to reject values outside 0-100% range.

```python
# AFTER (fixed)
def on_message(self, client, userdata, msg):
    speed = int(float(msg.payload.decode()))
    if speed < 0 or speed > 100:
        print(f"[FanControl] Invalid speed {speed}%, must be 0-100")
        return
    self.new_speed = speed
```

---

### 6. Race Condition in Control Loops

**Files:** All control classes

**Problem:** `new_speed` could be modified by MQTT callback thread between the check and use.

```python
# BEFORE (race condition)
if self.new_speed is not None and self.new_speed != self.old_speed:
    self.device.write_register(..., value=self.new_speed, ...)
    self.old_speed = self.new_speed
```

**Fix:** Copy to local variable before use.

```python
# AFTER (fixed)
speed = self.new_speed  # Local copy
if speed is not None and speed != self.old_speed:
    self.device.write_register(..., value=speed, ...)
    self.old_speed = speed
```

---

### 7. No Data Validation After Modbus Read

**File:** `sensor/read_HG803.py`

**Problem:** No check that returned data has expected length before indexing.

**Fix:** Added length validation.

```python
if len(data) < 2:
    print(f"[ReadHG803] Error: Expected 2 registers, got {len(data)}")
    return
```

---

### 8. MQTT Client Connects at Import Time

**File:** `common_config.py`

**Problem:** MQTT connection happened at module import. If broker unavailable, program crashes before any error handling.

**Fix:** Lazy initialization with error handling.

```python
# AFTER (fixed)
_mqtt_client = None

def create_client():
    global _mqtt_client
    if _mqtt_client is None:
        try:
            _mqtt_client = mqtt.Client(client_id="InletPi")
            _mqtt_client.connect(BROKER_IP, BROKER_PORT, 60)
        except Exception as e:
            print(f"[MQTT] Failed to connect: {e}")
            raise
    return _mqtt_client
```

---

### 9. Redundant Condition Check

**File:** `heater/relay_control.py`

**Problem:** Redundant `if` statement after early return.

**Fix:** Simplified logic.

---

## Code Quality Fixes

### 10. Typos in Method Names

| File | Before | After |
|------|--------|-------|
| `fan/fan_control.py` | `fan_initialzation()` | `fan_initialization()` |
| `pump/pump_control.py` | `pump_initialzation()` | `pump_initialization()` |
| `main_inlet.py` | Updated calls | Updated calls |

---

### 11. Broken Comment

**File:** `pump/pump_control.py`

Removed garbled copy-paste comment.

---

### 12. Typo in Print Statement

**File:** `powermeter/read_powermeter.py`

Fixed `Total Export:L` to `Total Export:`.

---

### 13. Inconsistent Print Statement Prefixes

Standardized all print statements to use consistent naming:
- `[FanControl]` (was `[FanControll]`, `[Fan Controll]`)
- `[PumpControl]` (was `[PumpControll]`)
- `[HeaterControl]` (was `[HeaterControll]`)

---

### 14. Instance Variable Used as Local

**File:** `pump/pump_control.py`

Changed `self.new_pump_speed` to local variable `pump_speed`.

---

### 15. Boolean Written to Register

**File:** `hotend/PIDcontroller_control.py`

Changed `value=True` and `value=False` to explicit `value=1` and `value=0` for clarity with hardware registers.

---

## Summary Table

| Priority | Issue | Status |
|----------|-------|--------|
| Critical | Shared MQTT disconnect | Fixed |
| Critical | Type annotation bug | Fixed |
| Critical | None parameter writes | Fixed |
| High | Debug mode enabled | User will remove |
| High | No input validation | Fixed |
| High | Race conditions | Fixed |
| Medium | Import-time MQTT connect | Fixed |
| Medium | No Modbus data validation | Fixed |
| Medium | Redundant condition | Fixed |
| Low | Method name typos | Fixed |
| Low | Broken comment | Fixed |
| Low | Print statement typos | Fixed |
| Low | Inconsistent naming | Fixed |
| Low | Unnecessary instance var | Fixed |
| Low | Boolean in register write | Fixed |
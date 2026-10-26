#!/usr/bin/env python3
"""
Car status helpers for Lab 2 WiFi / Bluetooth servers.

Tracks distance / last motion labels, reads Pi CPU temp, and (when available)
battery voltage from the Freenove ADC.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional


# Rough Li-ion pack mapping for Freenove 4WD (ADC channel 2 scaled voltage).
_BATTERY_V_EMPTY = 6.0
_BATTERY_V_FULL = 8.4


class CarTelemetry:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.distance_m = 0.0
        self.speed_mps = 0.0
        self.moving = "stopped"
        self.turning = "no"
        self._adc = None
        self._last_move_t = time.monotonic()

        if not dry_run:
            try:
                # Code/Server is on sys.path when launched from wifi_server
                from adc import ADC  # type: ignore

                self._adc = ADC()
            except Exception as e:
                print(f"[telemetry] ADC unavailable ({e}); battery will be N/A")

    def close(self) -> None:
        if self._adc is not None:
            try:
                self._adc.close_i2c()
            except Exception:
                pass
            self._adc = None

    def note_motion(
        self,
        moving: str,
        turning: str = "no",
        distance_delta_m: float = 0.0,
        duration_s: float = 0.0,
    ) -> None:
        self.moving = moving
        self.turning = turning
        if distance_delta_m > 0:
            self.distance_m += distance_delta_m
        if duration_s > 0 and distance_delta_m > 0:
            self.speed_mps = distance_delta_m / duration_s
        elif moving == "stopped":
            self.speed_mps = 0.0
        self._last_move_t = time.monotonic()

    def read_temp_c(self) -> Optional[float]:
        path = "/sys/class/thermal/thermal_zone0/temp"
        try:
            with open(path, "r", encoding="utf-8") as f:
                milli = int(f.read().strip())
            return round(milli / 1000.0, 1)
        except Exception:
            return None

    def read_battery_percent(self) -> Optional[float]:
        if self._adc is None:
            return None
        try:
            # Same formula as Freenove adc.py __main__
            pcb = self._adc.pcb_version
            volts = self._adc.read_adc(2) * (3 if pcb == 1 else 2)
            pct = (volts - _BATTERY_V_EMPTY) / (_BATTERY_V_FULL - _BATTERY_V_EMPTY) * 100.0
            return round(max(0.0, min(100.0, pct)), 1)
        except Exception:
            return None

    def snapshot(self) -> Dict[str, Any]:
        return {
            "battery": self.read_battery_percent(),
            "temp_c": self.read_temp_c(),
            "speed": round(self.speed_mps, 2),
            "distance": round(self.distance_m, 2),
            "moving": self.moving,
            "turning": self.turning,
        }

    def to_json_line(self) -> str:
        return json.dumps(self.snapshot(), separators=(",", ":")) + "\n"

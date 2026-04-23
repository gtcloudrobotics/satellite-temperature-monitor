"""Log-file assertions for the autograder.

Each check() runs ./build/satellite_monitor with the already-prepared
config.ini (the runner copies the right fixture before calling us), then
validates the resulting temperature_log.txt and fault_log.txt.

Every check returns a list of failure messages. Empty list == pass.
Collecting *all* failures per test (rather than bailing on the first)
gives students the complete picture in one run.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MONITOR = REPO / "build" / "satellite_monitor"
TEMP_LOG = REPO / "temperature_log.txt"
FAULT_LOG = REPO / "fault_log.txt"

REQUIRED_TARGETS = ("simulation_core", "app_support", "satellite_monitor")

TEMP_HEADER = "timestamp,temp1,temp2,average"
FAULT_HEADER = "timestamp,sensor,value"

TWO_DP = re.compile(r"^-?\d+\.\d{2}$")


def _run_monitor() -> list[str]:
    result = subprocess.run(
        [str(MONITOR), "--config", "config.ini"],
        cwd=REPO, capture_output=True, text=True,
    )
    if result.returncode != 0:
        msg = f"./build/satellite_monitor --config config.ini exited {result.returncode}"
        if result.stderr.strip():
            msg += f"\nstderr:\n{result.stderr.rstrip()}"
        return [msg]
    return []


def _read_csv(path: Path) -> tuple[str, list[list[str]]]:
    lines = path.read_text().splitlines()
    header = lines[0] if lines else ""
    rows = [line.split(",") for line in lines[1:]]
    return header, rows


def check_targets() -> list[str]:
    errs: list[str] = []
    for target in REQUIRED_TARGETS:
        result = subprocess.run(
            ["cmake", "--build", "build", "--target", target],
            cwd=REPO, capture_output=True, text=True,
        )
        if result.returncode != 0:
            errs.append(f"cmake --build --target {target} failed (missing or misnamed)")
    if not MONITOR.is_file() or not os.access(MONITOR, os.X_OK):
        errs.append("build/satellite_monitor not found or not executable")
    return errs


def _require_logs() -> list[str]:
    errs = []
    if not TEMP_LOG.exists():
        errs.append(f"{TEMP_LOG.name} was not written")
    if not FAULT_LOG.exists():
        errs.append(f"{FAULT_LOG.name} was not written")
    return errs


def check_zero_variance() -> list[str]:
    errs = _run_monitor()
    if errs:
        return errs
    errs = _require_logs()
    if errs:
        return errs

    t_header, t_rows = _read_csv(TEMP_LOG)
    f_header, f_rows = _read_csv(FAULT_LOG)

    if t_header != TEMP_HEADER:
        errs.append(f"temperature_log.txt header: got {t_header!r}, expected {TEMP_HEADER!r}")
    if f_header != FAULT_HEADER:
        errs.append(f"fault_log.txt header: got {f_header!r}, expected {FAULT_HEADER!r}")

    if len(t_rows) < 3:
        errs.append(f"expected >=3 temperature rows for 3s @ 1Hz, got {len(t_rows)}")

    for i, row in enumerate(t_rows, start=2):
        if len(row) != 4:
            errs.append(f"temperature_log.txt line {i}: {len(row)} fields, want 4 ({row!r})")
            continue
        _, t1, t2, avg = row
        if (t1, t2, avg) != ("25.00", "26.00", "25.50"):
            errs.append(
                f"temperature_log.txt line {i}: expected <ts>,25.00,26.00,25.50 — "
                f"got temp1={t1}, temp2={t2}, average={avg}"
            )

    if len(f_rows) != 0:
        errs.append(
            f"expected 0 fault rows (both sensor means in-range), got {len(f_rows)}"
        )

    return errs


def check_faults() -> list[str]:
    errs = _run_monitor()
    if errs:
        return errs
    errs = _require_logs()
    if errs:
        return errs

    _, t_rows = _read_csv(TEMP_LOG)
    _, f_rows = _read_csv(FAULT_LOG)

    expected = len(t_rows) * 2
    if len(f_rows) != expected:
        errs.append(
            f"expected {expected} fault rows ({len(t_rows)} data rows × 2 failing sensors), "
            f"got {len(f_rows)}"
        )

    sensors = {row[1] for row in f_rows if len(row) >= 2}
    for name in ("sensor_1", "sensor_2"):
        if name not in sensors:
            errs.append(f"{name} never appears in fault_log.txt")

    return errs


def check_real_noise() -> list[str]:
    errs = _run_monitor()
    if errs:
        return errs
    errs = _require_logs()
    if errs:
        return errs

    t_header, t_rows = _read_csv(TEMP_LOG)
    f_header, f_rows = _read_csv(FAULT_LOG)

    if t_header != TEMP_HEADER:
        errs.append(f"temperature_log.txt header: got {t_header!r}, expected {TEMP_HEADER!r}")
    if f_header != FAULT_HEADER:
        errs.append(f"fault_log.txt header: got {f_header!r}, expected {FAULT_HEADER!r}")

    if not (5 <= len(t_rows) <= 6):
        errs.append(f"expected 5 or 6 data rows for 5s @ 1Hz, got {len(t_rows)}")

    for i, row in enumerate(t_rows, start=2):
        if len(row) != 4:
            errs.append(f"temperature_log.txt line {i}: {len(row)} fields, want 4")
            continue
        bad_field = next(
            (j for j, field in enumerate(row, start=1) if not TWO_DP.match(field)),
            None,
        )
        if bad_field is not None:
            errs.append(
                f"temperature_log.txt line {i} field {bad_field}: "
                f"{row[bad_field - 1]!r} is not 2-decimal numeric"
            )
            continue
        t1, t2, avg = float(row[1]), float(row[2]), float(row[3])
        if abs(avg - (t1 + t2) / 2) > 0.01:
            errs.append(
                f"temperature_log.txt line {i}: average {avg} != (temp1+temp2)/2 "
                f"(= {(t1 + t2) / 2:.4f}), tolerance 0.01"
            )

    for i, row in enumerate(f_rows, start=2):
        if len(row) != 3:
            errs.append(f"fault_log.txt line {i}: {len(row)} fields, want 3")
            continue
        ts, sensor, value = row
        if sensor not in ("sensor_1", "sensor_2"):
            errs.append(f"fault_log.txt line {i}: bad sensor name {sensor!r}")
        if not TWO_DP.match(ts):
            errs.append(f"fault_log.txt line {i}: timestamp {ts!r} is not 2-decimal numeric")
        if not TWO_DP.match(value):
            errs.append(f"fault_log.txt line {i}: value {value!r} is not 2-decimal numeric")

    return errs

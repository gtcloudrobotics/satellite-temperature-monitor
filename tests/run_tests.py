#!/usr/bin/env python3
"""Autograder test runner — the same tests GitHub Actions runs.

Run this before you push to get instant pass/fail feedback instead
of waiting on a Classroom Actions run. Same tests, same exit code:
0 if everything passes, non-zero otherwise.

Usage (from the repository root):

    python3 tests/run_tests.py            # build, then run all tests
    python3 tests/run_tests.py --no-build # skip the cmake build step

"""

import argparse
import subprocess
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import checks  # noqa: E402  (sibling module, import after sys.path tweak)

REPO = Path(__file__).resolve().parent.parent

TESTS = [
    {
        "name": "Required CMake targets exist",
        "setup": None,
        "command": checks.check_targets,
        "checks": (
            "Your CMakeLists.txt must define three targets with these exact names:\n"
            "  - simulation_core    (library: sim logic, sensors, faults)\n"
            "  - app_support        (library: config parsing, log writing)\n"
            "  - satellite_monitor  (executable that wires the CLI to the libs)\n"
            "\n"
            "The grader runs `cmake --build build --target <name>` for each one,\n"
            "then verifies that build/satellite_monitor exists and is executable."
        ),
        "hints": [
            "Target names must match exactly — no typos, no prefixes, no suffixes",
            "satellite_monitor must be an add_executable, not a library",
            "Make sure the build output actually lands at build/satellite_monitor",
        ],
    },
    {
        "name": "--help exits successfully",
        "setup": None,
        "command": "./build/satellite_monitor --help",
        "checks": (
            "Running `./build/satellite_monitor --help` must exit with code 0.\n"
            "This confirms your CLI is reachable and that your argument parser\n"
            "handles --help as a first-class flag (not an error)."
        ),
        "hints": [
            "--help should print usage to stdout and exit 0 — not exit non-zero",
            "Handle --help BEFORE you try to load config.ini, or it'll fail before --help runs",
            "With Boost.Program_options, check options.count(\"help\") right after store/notify",
        ],
    },
    {
        "name": "Zero-variance run produces expected logs",
        "setup": "cp tests/configs/zero_variance.ini config.ini",
        "command": checks.check_zero_variance,
        "checks": (
            "Config: duration=3s, period=1000ms, both sensors stddev=0,\n"
            "means 25.0 and 26.0, fault range [18.0, 32.0].\n"
            "\n"
            "With no noise, every temperature row must be EXACTLY:\n"
            "  <timestamp>,25.00,26.00,25.50\n"
            "\n"
            "Headers must match exactly:\n"
            "  temperature_log.txt  ->  timestamp,temp1,temp2,average\n"
            "  fault_log.txt        ->  timestamp,sensor,value\n"
            "\n"
            "Both means are in-range, so fault_log.txt must have 0 data rows.\n"
            "Must emit at least 3 data rows for 3s @ 1Hz."
        ),
        "hints": [
            "Use 2-decimal formatting for every numeric column (25.00, not 25 or 25.0)",
            "No extra whitespace around commas — plain CSV",
            "Average is (temp1 + temp2) / 2 — computed per row",
            "Don't emit fault rows when readings are in-range",
            "Overwrite the log files on each run; don't append to previous output",
        ],
    },
    {
        "name": "Fault detection catches out-of-range sensors",
        "setup": "cp tests/configs/force_faults.ini config.ini",
        "command": checks.check_faults,
        "checks": (
            "Config: duration=2s, period=1000ms, sensor_1 mean=50 (above max),\n"
            "sensor_2 mean=10 (below min), both stddev=0, fault range [18.0, 32.0].\n"
            "\n"
            "Every reading is out of range on BOTH sensors, so:\n"
            "  fault_log data rows == temperature_log data rows * 2\n"
            "\n"
            "Both sensor names (sensor_1 and sensor_2) must appear in fault_log.txt."
        ),
        "hints": [
            "Emit ONE fault row per out-of-range reading — so 2 fault rows per step when both fail",
            "Use the literal strings `sensor_1` and `sensor_2` as the sensor column value",
            "Don't collapse duplicate faults — every out-of-range reading gets its own row",
            "A reading ABOVE max_valid_temp is just as much a fault as one BELOW min_valid_temp",
        ],
    },
    {
        "name": "Real-noise run produces well-formed logs",
        "setup": "cp tests/configs/real_noise.ini config.ini",
        "command": checks.check_real_noise,
        "checks": (
            "Config: duration=5s, period=1000ms, realistic stddevs around in-range means.\n"
            "\n"
            "Checks SHAPE, not statistics (fault count is probabilistic):\n"
            "  - temperature_log header: timestamp,temp1,temp2,average\n"
            "  - fault_log header:       timestamp,sensor,value\n"
            "  - 5 or 6 data rows (endpoint inclusive or exclusive at t=5s is fine)\n"
            "  - Every temperature row has exactly 4 numeric fields, each 2 decimal places\n"
            "  - average == (temp1 + temp2) / 2 within 0.01 tolerance\n"
            "  - Fault rows: 3 fields, valid sensor name, 2dp values"
        ),
        "hints": [
            "Format every number as %.2f — including negatives if your RNG produces any",
            "Pick one endpoint convention and stick with it (5 rows or 6 rows are both OK)",
            "No trailing commas or empty fields",
            "The average tolerance is 0.01 — don't round temp1/temp2 then re-average",
        ],
    },
]


def run_stream(cmd: str) -> int:
    """Run a command and let its output go straight to the terminal."""
    return subprocess.run(cmd, cwd=REPO, shell=True).returncode


def run_capture(cmd: str) -> tuple[int, str]:
    """Run a command, capture stdout+stderr together, return (rc, output)."""
    result = subprocess.run(
        cmd, cwd=REPO, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True,
    )
    return result.returncode, result.stdout


def indent(text: str, prefix: str = "    ") -> str:
    return textwrap.indent(text.rstrip(), prefix)


def print_failure(test: dict, stage: str, rc: int, output: str) -> None:
    print(f"  FAIL ({stage}, exit {rc})")
    print()
    print("  What this test checks:")
    print(indent(test["checks"]))
    print()
    if output.strip():
        print("  Actual output from the check:")
        print(indent(output))
        print()
    print("  Things to double-check:")
    for hint in test["hints"]:
        print(f"    - {hint}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()

    if not args.no_build:
        print("=== Building ===")
        if run_stream("cmake -S . -B build") or run_stream("cmake --build build"):
            print("\nBUILD FAILED — fix the compilation errors above before running tests.")
            return 1

    failed = []
    for test in TESTS:
        print(f"\n=== {test['name']} ===")

        if test["setup"]:
            rc, output = run_capture(test["setup"])
            if rc != 0:
                print_failure(test, "setup", rc, output)
                failed.append(test["name"])
                continue

        command = test["command"]
        if callable(command):
            errs = command()
            rc = 1 if errs else 0
            output = "\n".join(errs)
        else:
            rc, output = run_capture(command)

        if rc == 0:
            print("  PASS")
        else:
            print_failure(test, "test", rc, output)
            failed.append(test["name"])

    print(f"\n=== {len(TESTS) - len(failed)}/{len(TESTS)} passed ===")
    for n in failed:
        print(f"  FAIL: {n}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

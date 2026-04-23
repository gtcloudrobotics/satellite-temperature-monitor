# C++ CLI Tooling: Satellite Temperature Monitor

Build a small C++ program that simulates a satellite temperature monitor.

The system has two redundant temperature sensors. On each simulation step, generate one reading from each sensor, compute their average, and detect whether either sensor is out of range.

## Requirements

- Use C++ and CMake.
- Name the executable `satellite_monitor`.
- Provide a `CMakeLists.txt` that defines these CMake targets:
	- `simulation_core`
	- `app_support`
	- `satellite_monitor`
- Use Boost.Program_options to load settings from an INI file.
- Use CMake to find and link `Boost::program_options`.
- Support a small, clear command-line interface.
- Run in fixed simulation steps, not real time.
- Overwrite output files on each run.

Use this split:

- `simulation_core` for simulation logic, such as sensor generation, averaging, and fault detection
- `app_support` for application support, such as config parsing and log writing
- `satellite_monitor` as a thin executable that wires the CLI to those libraries

The autograder will check target names directly, so use these names exactly.

## How Your Program Will Be Built and Run

Your program will be built from the repository root like this:

```sh
cmake -S . -B build
cmake --build build
```

After that, it should support these forms:

```sh
./build/satellite_monitor
./build/satellite_monitor --config config.ini
./build/satellite_monitor --help
```

Rules:

- If no arguments are provided, read `config.ini` from the current working directory.
- `--config <path>` loads the specified config file.
- `--help` prints a short usage message describing the supported options and exits successfully.
- Invalid arguments should print a useful error message and exit non-zero.

## Config File

Use this INI shape:

```ini
[simulation]
simulation_duration_s = 10
sample_period_ms = 1000
random_seed = 12345

[sensor_1]
mean = 25.0
stddev = 2.0

[sensor_2]
mean = 26.0
stddev = 1.5

[fault_detection]
min_valid_temp = 18.0
max_valid_temp = 32.0
```

## Output Files

Write `temperature_log.txt` with this exact header:

```text
timestamp,temp1,temp2,average
```

Write `fault_log.txt` with this exact header:

```text
timestamp,sensor,value
```

Rules:

- `timestamp` is simulated time in seconds, starting at `0.00`
- numeric values use two decimal places
- `average` is `(temp1 + temp2) / 2`
- write one fault row for each out-of-range sensor reading
- use `sensor_1` and `sensor_2` as sensor names in the fault log

## Error Handling

- If the config file is missing, unreadable, or invalid, print a useful error to stderr and exit non-zero.
- Otherwise exit 0.

## Deliverables

- source code
- `CMakeLists.txt`
- `config.ini`
- a short README describing your design decisions

In your README, briefly explain how you split the project into CMake targets.

## Running the Autograder Locally

You can run the exact same tests GitHub Classroom runs, locally, before you push. From the repository root:

```sh
python3 tests/run_tests.py            # build, then run all tests
python3 tests/run_tests.py --no-build # skip the cmake build step
```

Exit code is `0` if every test passes, non-zero otherwise — same contract as CI.

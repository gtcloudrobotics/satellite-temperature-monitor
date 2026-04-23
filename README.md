# Satellite Temperature Monitor

Build a C++ program that simulates a satellite temperature monitor. It reads a config file, runs a fixed-step simulation over two redundant sensors, and writes two CSV logs to disk.

You'll create all the source files yourself. The repo ships with a `tests/` folder and nothing else.

## What to build

A single executable called `satellite_monitor`. Your `CMakeLists.txt` must define three targets with these exact names (the autograder builds each one by name):

- `simulation_core` (library): sensor generation, averaging, fault detection
- `app_support` (library): config parsing, log writing
- `satellite_monitor` (executable): wires the CLI to the two libraries

Use `find_package` to locate Boost and link `Boost::program_options`.

## Config file

Your program reads an INI file via Boost.Program_options. The autograder drops its own config at `config.ini` before each test, so your program needs to accept this layout:

```ini
[simulation]
simulation_duration_s = 5
sample_period_ms = 1000
random_seed = 42

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

To run the program manually, point `--config` at one of the test fixtures, e.g. `--config tests/configs/real_noise.ini`.

## CLI

The autograder runs your program as:

```sh
./build/satellite_monitor --config config.ini
```

It also runs `--help`, which must exit 0. Check for `--help` before you open the config file, otherwise `--help` fails when `config.ini` doesn't exist yet.

## Simulation

The simulation runs in discrete steps, not real time. Step count is `simulation_duration_s * 1000 / sample_period_ms` so 5 seconds at 1000 ms/step gives 5 steps.

Each step: draw a temperature from each sensor's normal distribution (seeded with `random_seed` using `std::default_random_engine`), compute the average from the raw values, then check each reading against the fault range. If a reading falls outside `[min_valid_temp, max_valid_temp]`, it's a fault. Both sensors are checked independently, so a single step can produce zero, one, or two fault rows.

The timestamp is elapsed time in seconds, formatted to 2 decimal places. Starting at step 1 or step 0 is both fine; 5 or 6 rows for a 5-second run are accepted.

## Output

Both files are written to the repo root and overwritten on every run.

`temperature_log.txt`, one row per step:

```
timestamp,temp1,temp2,average
1.00,25.00,26.00,25.50
2.00,25.00,26.00,25.50
```

`fault_log.txt`, one row per out-of-range reading (zero rows is valid):

```
timestamp,sensor,value
1.00,sensor_1,50.00
1.00,sensor_2,10.00
```

Every numeric value is formatted to exactly 2 decimal places. No spaces around commas. The sensor column is the literal string `sensor_1` or `sensor_2`.

## Building and testing

```sh
mkdir build
cd build
cmake ..
make
```

Run the autograder tests locally before pushing:

```sh
python3 tests/run_tests.py
```

Local pass = CI pass. Each failing test prints what it checked, what it got, and hints on what to fix.

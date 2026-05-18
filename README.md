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

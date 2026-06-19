#include "app_support.h"
#include "simulation_core.h"
#include <boost/program_options.hpp>
#include <iostream>

namespace po = boost::program_options;

int main(int argc, char** argv) {
    try {
        po::options_description desc("Options");
        desc.add_options()
            ("help,h",   "Show this help message")
            ("config,c", po::value<std::string>()->required(), "Path to INI config file");

        po::variables_map vm;
        po::store(po::parse_command_line(argc, argv, desc), vm);

        if (vm.count("help")) {
            std::cout << desc << "\n";
            return 0;
        }

        po::notify(vm);

        Config cfg = load_config(vm["config"].as<std::string>());

        SimulationCore sim(
            cfg.sensor1_mean, cfg.sensor1_stddev,
            cfg.sensor2_mean, cfg.sensor2_stddev,
            cfg.min_valid_temp, cfg.max_valid_temp,
            cfg.random_seed);

        Logger logger("temperature_log.txt", "fault_log.txt");

        int steps = cfg.simulation_duration_s * 1000 / cfg.sample_period_ms;
        for (int i = 1; i <= steps; ++i) {
            double timestamp = i * cfg.sample_period_ms / 1000.0;
            SensorReading reading = sim.step();
            logger.write_temperature(timestamp, reading.temp1, reading.temp2, reading.average);
            for (const auto& fault : sim.check_faults(timestamp, reading))
                logger.write_fault(fault.timestamp, fault.sensor, fault.value);
        }

        return 0;
    } catch (const std::exception& e) {
        std::cerr << "error: " << e.what() << "\n";
        return 1;
    }
}

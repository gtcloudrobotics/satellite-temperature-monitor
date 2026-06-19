#include "app_support.h"
#include <boost/program_options.hpp>
#include <fstream>
#include <iomanip>
#include <stdexcept>

namespace po = boost::program_options;

Config load_config(const std::string& path) {
    po::options_description desc;
    desc.add_options()
        ("simulation.simulation_duration_s", po::value<int>()->required())
        ("simulation.sample_period_ms",      po::value<int>()->required())
        ("simulation.random_seed",           po::value<unsigned int>()->required())
        ("sensor_1.mean",                    po::value<double>()->required())
        ("sensor_1.stddev",                  po::value<double>()->required())
        ("sensor_2.mean",                    po::value<double>()->required())
        ("sensor_2.stddev",                  po::value<double>()->required())
        ("fault_detection.min_valid_temp",   po::value<double>()->required())
        ("fault_detection.max_valid_temp",   po::value<double>()->required());

    std::ifstream ifs(path);
    if (!ifs)
        throw std::runtime_error("config file not found: " + path);

    po::variables_map vm;
    po::store(po::parse_config_file(ifs, desc), vm);
    po::notify(vm);

    Config cfg;
    cfg.simulation_duration_s = vm["simulation.simulation_duration_s"].as<int>();
    cfg.sample_period_ms      = vm["simulation.sample_period_ms"].as<int>();
    cfg.random_seed           = vm["simulation.random_seed"].as<unsigned int>();
    cfg.sensor1_mean          = vm["sensor_1.mean"].as<double>();
    cfg.sensor1_stddev        = vm["sensor_1.stddev"].as<double>();
    cfg.sensor2_mean          = vm["sensor_2.mean"].as<double>();
    cfg.sensor2_stddev        = vm["sensor_2.stddev"].as<double>();
    cfg.min_valid_temp        = vm["fault_detection.min_valid_temp"].as<double>();
    cfg.max_valid_temp        = vm["fault_detection.max_valid_temp"].as<double>();
    return cfg;
}

Logger::Logger(const std::string& temperature_path, const std::string& fault_path) {
    temperature_log_.open(temperature_path);
    fault_log_.open(fault_path);
    if (!temperature_log_)  throw std::runtime_error("cannot open " + temperature_path);
    if (!fault_log_) throw std::runtime_error("cannot open " + fault_path);
    temperature_log_  << "timestamp,temp1,temp2,average\n";
    fault_log_ << "timestamp,sensor,value\n";
}

void Logger::write_temperature(double timestamp, double temp1, double temp2, double average) {
    temperature_log_ << std::fixed << std::setprecision(2)
               << timestamp << "," << temp1 << "," << temp2 << "," << average << "\n";
}

void Logger::write_fault(double timestamp, const std::string& sensor, double value) {
    fault_log_ << std::fixed << std::setprecision(2)
                << timestamp << "," << sensor << "," << value << "\n";
}

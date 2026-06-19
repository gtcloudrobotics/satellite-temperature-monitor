#pragma once
#include <fstream>
#include <string>

struct Config {
    int simulation_duration_s;
    int sample_period_ms;
    unsigned int random_seed;
    double sensor1_mean;
    double sensor1_stddev;
    double sensor2_mean;
    double sensor2_stddev;
    double min_valid_temp;
    double max_valid_temp;
};

Config load_config(const std::string& path);

class Logger {
public:
    Logger(const std::string& temperature_path, const std::string& fault_path);
    void write_temperature(double timestamp, double temp1, double temp2, double average);
    void write_fault(double timestamp, const std::string& sensor, double value);

private:
    std::ofstream temperature_log_;
    std::ofstream fault_log_;
};

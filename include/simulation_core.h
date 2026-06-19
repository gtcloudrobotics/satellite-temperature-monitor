#pragma once
#include <random>
#include <string>
#include <vector>

struct SensorReading {
    double temp1;
    double temp2;
    double average;
};

struct FaultRecord {
    double timestamp;
    std::string sensor;
    double value;
};

class SimulationCore {
public:
    SimulationCore(double mean1, double stddev1,
                   double mean2, double stddev2,
                   double min_temp, double max_temp,
                   unsigned int seed);

    SensorReading step();
    std::vector<FaultRecord> check_faults(double timestamp, const SensorReading& reading) const;

private:
    std::default_random_engine random_engine_;
    double stddev1_, stddev2_;
    std::normal_distribution<double> dist1_;
    std::normal_distribution<double> dist2_;
    double min_temp_;
    double max_temp_;
};

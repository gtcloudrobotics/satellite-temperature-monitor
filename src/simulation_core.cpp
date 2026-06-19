#include "simulation_core.h"

SimulationCore::SimulationCore(double mean1, double stddev1,
                               double mean2, double stddev2,
                               double min_temp, double max_temp,
                               unsigned int seed)
    : random_engine_(seed),
      stddev1_(stddev1), stddev2_(stddev2),
      min_temp_(min_temp),
      max_temp_(max_temp) {
    // std::normal_distribution is undefined for stddev=0, so use a dummy
    // value and bypass it in step() when stddev is zero
    double safe_stddev1 = 1.0;
    if (stddev1 > 0.0) safe_stddev1 = stddev1;

    double safe_stddev2 = 1.0;
    if (stddev2 > 0.0) safe_stddev2 = stddev2;
    dist1_ = std::normal_distribution<double>(mean1, safe_stddev1);
    dist2_ = std::normal_distribution<double>(mean2, safe_stddev2);
}

SensorReading SimulationCore::step() {
    double temp1;
    if (stddev1_ == 0.0)
        temp1 = dist1_.mean();
    else
        temp1 = dist1_(random_engine_);

    double temp2;
    if (stddev2_ == 0.0)
        temp2 = dist2_.mean();
    else
        temp2 = dist2_(random_engine_);

    double average = (temp1 + temp2) / 2.0;
    return {temp1, temp2, average};
}

std::vector<FaultRecord> SimulationCore::check_faults(double timestamp, const SensorReading& r) const {
    std::vector<FaultRecord> faults;
    if (r.temp1 < min_temp_ || r.temp1 > max_temp_)
        faults.push_back({timestamp, "sensor_1", r.temp1});
    if (r.temp2 < min_temp_ || r.temp2 > max_temp_)
        faults.push_back({timestamp, "sensor_2", r.temp2});
    return faults;
}

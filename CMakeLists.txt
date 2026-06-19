cmake_minimum_required(VERSION 3.15)
project(satellite_temperature_monitor CXX)
set(CMAKE_CXX_STANDARD 17)

find_package(Boost REQUIRED COMPONENTS program_options)

add_library(simulation_core src/simulation_core.cpp)
target_include_directories(simulation_core PUBLIC include)

add_library(app_support src/app_support.cpp)
target_include_directories(app_support PUBLIC include)
target_link_libraries(app_support PUBLIC Boost::program_options)

add_executable(satellite_monitor src/main.cpp)
target_link_libraries(satellite_monitor PRIVATE simulation_core app_support)

cmake_minimum_required(VERSION 3.15)
project(test_module_config CXX)

find_package(Fontconfig)

add_executable(test_module_config src/test_module_config.cpp src/main.cpp)
target_include_directories(test_module_config PUBLIC include)

target_link_libraries(test_module_config PUBLIC Fontconfig::Fontconfig)

install(TARGETS test_module_config)

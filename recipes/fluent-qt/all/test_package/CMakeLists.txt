cmake_minimum_required(VERSION 3.16)
project(FluentQtConanConsumer LANGUAGES CXX)

find_package(FluentQt CONFIG REQUIRED)
add_executable(consumer main.cpp)
target_compile_features(consumer PRIVATE cxx_std_17)
target_link_libraries(consumer PRIVATE FluentQt::FluentQt)

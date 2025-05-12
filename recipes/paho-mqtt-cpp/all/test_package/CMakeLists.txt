cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

find_package(PahoMqttCpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
target_link_libraries(${PROJECT_NAME} PRIVATE
        $<$<TARGET_EXISTS:PahoMqttCpp::paho-mqttpp3>:PahoMqttCpp::paho-mqttpp3>
        $<$<NOT:$<TARGET_EXISTS:PahoMqttCpp::paho-mqttpp3>>:PahoMqttCpp::paho-mqttpp3-static>)

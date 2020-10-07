cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(PahoMqttCpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
if(PAHO_MQTT_CPP_SHARED)
  target_link_libraries(${PROJECT_NAME} PahoMqttCpp::paho-mqttpp3)
else()
  target_link_libraries(${PROJECT_NAME} PahoMqttCpp::paho-mqttpp3-static)
endif()

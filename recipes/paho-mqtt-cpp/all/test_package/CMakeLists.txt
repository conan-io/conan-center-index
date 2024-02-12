cmake_minimum_required(VERSION 3.8)

project(test_package C CXX)

find_package(PahoMqttCpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if(TEST_SSL_OPTION)
    target_compile_definitions(${PROJECT_NAME} PRIVATE TEST_SSL_OPTION)
endif()

if(PAHO_MQTT_CPP_SHARED)
  target_link_libraries(${PROJECT_NAME} PahoMqttCpp::paho-mqttpp3)
else()
  target_link_libraries(${PROJECT_NAME} PahoMqttCpp::paho-mqttpp3-static)
endif()

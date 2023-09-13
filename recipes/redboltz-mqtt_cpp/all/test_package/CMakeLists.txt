cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(mqtt_cpp_iface REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} mqtt_cpp_iface::mqtt_cpp_iface)
if(TEST_ENABLE_STD_CONTAINERS)
     target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
else()
     target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
endif()

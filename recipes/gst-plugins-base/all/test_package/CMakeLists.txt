cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(gst-plugins-base CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} gst-plugins-base::gstreamer-plugins-base-1.0)

cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(libxml++ REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(TARGET libxml++::libxml++-2.6)
    target_link_libraries(${PROJECT_NAME} libxml++::libxml++-2.6)
else()
    target_link_libraries(${PROJECT_NAME} libxml++::libxml++-5.0)
endif()

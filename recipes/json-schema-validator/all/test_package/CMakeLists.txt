cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(nlohmann_json_schema_validator CONFIG REQUIRED)

add_executable(example example.cpp)
set_property(TARGET example PROPERTY CXX_STANDARD 11)
target_link_libraries(example nlohmann_json_schema_validator)

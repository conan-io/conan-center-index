cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(open_simulation_interface REQUIRED)
find_package(Protobuf REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example
  protobuf::libprotobuf
  open_simulation_interface::open_simulation_interface
  )

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME example
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND example)
